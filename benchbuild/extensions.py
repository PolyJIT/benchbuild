"""
Extension base-classes for compile-time and run-time experiments.
"""
import logging
import os
import typing as t
from abc import ABCMeta
from collections import Iterable

import parse
from plumbum import local

import yaml
from benchbuild.utils.db import persist_config, persist_time
from benchbuild.utils.run import RunInfo, fetch_time_output, track_execution

LOG = logging.getLogger(__name__)


class Extension(metaclass=ABCMeta):
    """An experiment functor to implement composable experiments.

    An experiment extension is always callable with an arbitrary amount of
    arguments. The varargs component of an extension's `__call__` operator
    is fed the binary command that we currently execute and all arguments
    to the binary.
    Any customization necessary for the extension (e.g, dynamic configuration
    options) has to be passed by keyword argument.

    Args:
        *extensions: Variable length list of child extensions we manage.
        config (:obj:`dict`, optional): Dictionary of name value pairs to be
            stored for this extension.

    Attributes:
        next_extensions: Variable length list of child extensions we manage.
        config (:obj:`dict`, optional): Dictionary of name value pairs to be
            stored for this extension.
    """

    def __init__(self, *extensions, config=None, **kwargs):
        """Initialize an extension with an arbitrary number of children."""
        del kwargs
        self.next_extensions = extensions
        self.config = config

    def call_next(self, *args, **kwargs) -> t.List[RunInfo]:
        """Call all child extensions with the given arguments.

        This calls all child extensions and collects the results for
        our own parent. Use this to control the execution of your
        nested extensions from your own extension.

        Returns:
            :obj:`list` of :obj:`RunInfo`: A list of collected
                results of our child extensions.
        """
        all_results = []
        for ext in self.next_extensions:
            LOG.debug("  ++ - %s ", ext.__class__)
            results = ext(*args, **kwargs)
            LOG.debug("  -- - %s => %s", ext.__class__, results)
            if results is None:
                LOG.warning("No result from: %s", ext.__class__)
                continue
            result_list = []
            if isinstance(results, Iterable):
                result_list.extend(results)
            else:
                result_list.append(results)
            status_list = [r.db_run.status for r in result_list]
            LOG.debug("  -- %s - %s => %s", str(status_list), ext.__class__,
                      results)

            all_results.extend(result_list)

        return all_results

    def __lshift__(self, rhs):
        rhs.next_extensions = [self]
        return rhs

    def print(self, indent=0):
        """Print a structural view of the registered extensions."""
        LOG.info("%s:: %s", indent * " ", self.__class__)
        for ext in self.next_extensions:
            ext.print(indent=indent + 2)

    def __call__(self, *args, **kwargs):
        return self.call_next(*args, **kwargs)


class RuntimeExtension(Extension):
    """
    Default extension to execute and track a binary.

    This can be used for runtime experiments to have a controlled,
    tracked execution of a wrapped binary.
    """

    def __init__(self, project, experiment, *extensions, config=None):
        self.project = project
        self.experiment = experiment

        super(RuntimeExtension, self).__init__(*extensions, config=config)

    def __call__(self, binary_command, *args, **kwargs):
        self.project.name = kwargs.get("project_name", self.project.name)

        cmd = binary_command[args]
        with track_execution(cmd, self.project, self.experiment,
                             **kwargs) as run:
            run_info = run()
            if self.config:
                LOG.info("")
                LOG.info("==CONFIG==")
                LOG.info(
                    yaml.dump(
                        self.config,
                        width=40,
                        indent=4,
                        default_flow_style=False))
                LOG.info("==CONFIG==")
                LOG.info("")
                self.config['baseline'] = \
                    os.getenv("BB_IS_BASELINE", "False")
                persist_config(run_info.db_run, run_info.session, self.config)
        res = self.call_next(binary_command, *args, **kwargs)
        res.append(run_info)
        return res


class RunWithTimeout(Extension):
    """
    Guard a binary with a timeout.

    This wraps a any binary with a call to `timeout` and sets
    the limit to a given value on extension construction.
    """

    def __init__(self, *extensions, limit="10m", **kwargs):
        super(RunWithTimeout, self).__init__(*extensions, **kwargs)
        self.limit = limit

    def __call__(self, binary_command, *args, **kwargs):
        from benchbuild.utils.cmd import timeout
        return self.call_next(timeout[self.limit, binary_command], *args,
                              **kwargs)


class LogTrackingMixin(object):
    """Add log-registering capabilities to extensions."""
    _logs = []

    def add_log(self, path):
        """
        Add a log to the tracked list.

        Args:
            path (str): Filename of a new log we want to track.
        """
        self._logs.append(path)

    @property
    def logs(self):
        """Return list of tracked logs."""
        return self._logs


class LogAdditionals(Extension):
    """Log any additional log files that were registered."""

    def __call__(self, *args, **kwargs):
        from benchbuild.utils.cmd import cat
        from plumbum import FG
        if not self.next_extensions:
            return None

        res = self.call_next(*args, **kwargs)

        for ext in self.next_extensions:
            if issubclass(ext.__class__, (LogTrackingMixin)):
                for log in ext.logs:
                    LOG.debug("Dumping content of '%s'.", log)
                    (cat[log] & FG)
                    LOG.debug("Dumping content of '%s' complete.", log)

        return res


class RunWithTime(Extension):
    """Wrap a command with time and store the timings in the database."""

    def __call__(self, binary_command, *args, may_wrap=True, **kwargs):
        from benchbuild.utils.cmd import time
        time_tag = "BENCHBUILD: "
        if may_wrap:
            run_cmd = time["-f", time_tag + "%U-%S-%e", binary_command]

        def handle_timing(run_infos):
            """Takes care of the formating for the timing statistics."""
            from benchbuild.utils import schema as s

            session = s.Session()
            for run_info in run_infos:
                if may_wrap:
                    timings = fetch_time_output(time_tag,
                                                time_tag + "{:g}-{:g}-{:g}",
                                                run_info.stderr.split("\n"))
                    if timings:
                        persist_time(run_info.db_run, session, timings)
                    else:
                        LOG.warning("No timing information found.")
            session.commit()
            return run_infos

        res = self.call_next(run_cmd, *args, **kwargs)
        return handle_timing(res)


class ExtractCompileStats(Extension):
    """Extract LLVM's compilation stats.

    This extension extracts the output of LLVM's '-stats' option.
    You can control the tracked statistics by using the sections
    `cs.components` and `cs.names` in the configuration.

    Furthermore, this runs the compiler and tracks the state in the databse,
    similar to RunCompiler.
    """

    def __init__(self, project, experiment, *extensions, config=None):
        self.project = project
        self.experiment = experiment

        super(ExtractCompileStats, self).__init__(*extensions, config=config)

    @staticmethod
    def get_compilestats(prog_out):
        """ Get the LLVM compilation stats from :prog_out:. """

        stats_pattern = parse.compile("{value:d} {component} - {desc}\n")

        for line in prog_out.split("\n"):
            if line:
                try:
                    res = stats_pattern.search(line + "\n")
                except ValueError:
                    LOG.warning("Triggered a parser exception for: '%s'\n",
                                line)
                    res = None
                if res is not None:
                    yield res

    def __call__(self,
                 cc,
                 *args,
                 project=None,
                 **kwargs):
        from benchbuild.experiments.compilestats import CompileStat
        from benchbuild.utils.db import persist_compilestats
        from benchbuild.utils.schema import Session
        from benchbuild.settings import CFG

        if project:
            self.project = project

        original_command = cc[args]
        clang = cc["-Qunused-arguments"]
        clang = clang[args]
        clang = clang[project.cflags]
        clang = clang[project.ldflags]
        clang = clang["-mllvm", "-stats"]

        run_config = self.config
        session = Session()
        with track_execution(clang, self.project, self.experiment) as run:
            run_info = run()
            if run_config is not None:
                persist_config(run_info.db_run, session, run_config)

            if not run_info.has_failed:
                stats = []
                cls = ExtractCompileStats
                for stat in cls.get_compilestats(run_info.stderr):
                    compile_s = CompileStat()
                    compile_s.name = stat["desc"].rstrip()
                    compile_s.component = stat["component"].rstrip()
                    compile_s.value = stat["value"]
                    stats.append(compile_s)

                components = CFG["cs"]["components"].value()
                names = CFG["cs"]["names"].value()

                stats = [s for s in stats if str(s.component) in components] \
                    if components is not None else stats
                stats = [s for s in stats if str(s.name) in names] \
                    if names is not None else stats

                if stats:
                    for stat in stats:
                        LOG.info(" [%s] %s = %s", stat.component, stat.name,
                                 stat.value)
                    persist_compilestats(run_info.db_run, run_info.session,
                                         stats)
                else:
                    LOG.info("No compilestats left, after filtering.")
                    LOG.warning("  Components: %s", components)
                    LOG.warning("  Names:      %s", names)
            else:
                with track_execution(original_command, self.project,
                                     self.experiment, **kwargs) as run:
                    LOG.warning("Fallback to: %s", str(original_command))
                    run_info = run()

        ret = self.call_next(cc, *args, **kwargs)
        ret.append(run_info)
        session.commit()
        return ret


class RunCompiler(Extension):
    """Default extension for compiler execution.

    This extension silences a few warnings, e.g., unused-arguments and
    handles database tracking for compiler commands. It is used as the default
    action for compiler execution.
    """

    def __init__(self, project, experiment, *extensions, config=None):
        self.project = project
        self.experiment = experiment

        super(RunCompiler, self).__init__(*extensions, config=config)

    def __call__(self,
                 command,
                 *args,
                 project=None,
                 rerun_on_error=True,
                 **kwargs):
        if project:
            self.project = project

        original_command = command[args]
        new_command = command["-Qunused-arguments"]
        new_command = new_command[args]
        new_command = new_command[self.project.cflags]
        new_command = new_command[self.project.ldflags]

        with track_execution(new_command, self.project, self.experiment,
                             **kwargs) as run:
            run_info = run()
            if self.config:
                LOG.info(
                    yaml.dump(
                        self.config,
                        width=40,
                        indent=4,
                        default_flow_style=False))
                persist_config(run_info.db_run, run_info.session, self.config)

            if run_info.has_failed:
                with track_execution(original_command, self.project,
                                     self.experiment, **kwargs) as run:
                    LOG.warning("Fallback to: %s", str(original_command))
                    run_info = run()

        res = self.call_next(new_command, *args, **kwargs)
        res.append(run_info)
        return res


class SetThreadLimit(Extension):
    """Sets the OpenMP thread limit, based on your settings.

    This extension uses the 'jobs' settings and controls the environment
    variable OMP_NUM_THREADS.
    """

    def __call__(self, binary_command, *args, **kwargs):
        from benchbuild.settings import CFG

        config = self.config
        if config is not None and 'jobs' in config.keys():
            jobs = config['jobs']
        else:
            LOG.warning("Parameter 'config' was unusable, using defaults")
            jobs = CFG["jobs"].value()

        ret = None
        with local.env(OMP_NUM_THREADS=str(jobs)):
            ret = self.call_next(binary_command, *args, **kwargs)
        return ret


class Rerun(Extension):
    pass