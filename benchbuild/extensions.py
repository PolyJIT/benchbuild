"""
Extension base-classes for compile-time and run-time experiments.
"""
import logging
from abc import ABCMeta, abstractmethod
from collections import Iterable

import parse
from plumbum import local
from benchbuild.utils.run import (track_execution,
                                  handle_stdin,
                                  fetch_time_output)
from benchbuild.utils.db import persist_config, persist_time

LOG = logging.getLogger(__name__)


class Extension(metaclass=ABCMeta):
    def __init__(self, *extensions, config=None, **kwargs):
        """Initialize an extension with an arbitrary number of children."""
        self.next_extensions = extensions
        self.config = config

    def call_next(self, *args, **kwargs):
        """Call all child extensions with the same arguments."""
        all_results = []
        for ext in self.next_extensions:
            LOG.debug("Invoking - %s " % ext.__class__)
            result = ext(*args, **kwargs)
            LOG.debug("Completed - %s => %s" % (ext.__class__, result))
            if result is None:
                LOG.warning("No result from: %s" % ext.__class__)
                continue
            if isinstance(result, Iterable):
                all_results.extend(result)
            else:
                all_results.append(result)
        return all_results

    def print(self, indent=0):
        """Print a structural view of the registered extensions."""
        LOG.info("{}:: {}".format(indent * " ", self.__class__))
        for ext in self.next_extensions:
            ext.print(indent=indent+2)

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Must provide implementation in subclass")

class RuntimeExtension(Extension):
    def __init__(self, project, experiment, *extensions, config=None):
        self.project = project
        self.experiment = experiment

        super(RuntimeExtension, self).__init__(*extensions, config=config)

    def __call__(self, binary_command, *args, **kwargs):
        self.project.name = kwargs.get("project_name", self.project.name)

        cmd = handle_stdin(binary_command, kwargs)
        with track_execution(cmd, self.project,
                             self.experiment, **kwargs) as run:
            run_info = run()
            if self.config:
                persist_config(run_info.db_run, run_info.session, self.config)
        res = self.call_next(binary_command, *args, **kwargs)
        res.append(run_info)
        return res


class LogTrackingMixin(object):
    """Add log-registering capabilities to extensions."""
    _logs = []

    def add_log(self, path):
        self._logs.append(path)

    @property
    def logs(self):
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
                LOG.debug("Checking additional log files from: {}".format(ext))
                for log in ext.logs:
                    LOG.debug("Dumping content of '{}'.".format(log))
                    cat[log] & FG
                    LOG.debug("Dumping content of '{}' complete.".format(log))

        return res


class RunWithTime(Extension):
    """Wrap a command with time and store the timings in the database."""
    def __call__(self, binary_command, *args, may_wrap=True, **kwargs):
        from benchbuild.utils.cmd import time
        run_cmd = local[binary_command]
        run_cmd = run_cmd[args]
        time_tag = "BENCHBUILD: "
        if may_wrap:
            run_cmd = time["-f", time_tag + "%U-%S-%e", run_cmd]

        def handle_timing(run_infos):
            """Takes care of the formating for the timing statistics."""
            from benchbuild.utils import schema as s

            session = s.Session()
            for run_info in run_infos:
                LOG.debug("Persisting time for '{}'".format(run_info))
                if may_wrap:
                    timings = fetch_time_output(
                        time_tag,
                        time_tag + "{:g}-{:g}-{:g}",
                        run_info.stderr.split("\n"))
                    if timings:
                        persist_time(run_info.db_run, session, timings)
                    else:
                        LOG.warning("No timing information found.")
            return run_infos

        res = self.call_next(run_cmd, *args, **kwargs)
        return handle_timing(res)


class ExtractCompileStats(Extension):
    def __init__(self, project, experiment, *extensions, config=None):
        self.project = project
        self.experiment = experiment

        super(ExtractCompileStats, self).__init__(*extensions, config=config)

    def get_compilestats(self, prog_out):
        """ Get the LLVM compilation stats from :prog_out:. """

        stats_pattern = parse.compile("{value:d} {component} - {desc}\n")

        for line in prog_out.split("\n"):
            if line:
                try:
                    res = stats_pattern.search(line + "\n")
                except ValueError:
                    LOG.warning(
                        "Triggered a parser exception for: '" + line + "'\n")
                    res = None
                if res is not None:
                    yield res

    def __call__(self, cc, *args, **kwargs):
        from benchbuild.utils.schema import CompileStat
        from benchbuild.utils.db import persist_compilestats
        from benchbuild.settings import CFG

        clang = handle_stdin(cc["-mllvm", "-stats"], kwargs)
        run_config = kwargs.get("run_config", None)

        with local.env(BB_ENABLE=0):
            with track_execution(clang, self.project, self.experiment) as run:
                run_info = run()
                if run_config is not None:
                    persist_config(
                        run_info.db_run, run_info.session, run_config)

        if run_info.retcode == 0:
            stats = []
            for stat in self.get_compilestats(run_info.stderr):
                compile_s = CompileStat()
                compile_s.name = stat["desc"].rstrip()
                compile_s.component = stat["component"].rstrip()
                compile_s.value = stat["value"]
                stats.append(compile_s)

            components = CFG["cs"]["components"].value()
            if components is not None:
                stats = [s for s in stats if str(s.component) in components]
            names = CFG["cs"]["names"].value()
            if names is not None:
                stats = [s for s in stats if str(s.name) in names]
            if stats:
                persist_compilestats(run_info.db_run, run_info.session, stats)
            else:
                LOG.info("No compilestats collected.")
        else:
            LOG.info("There was an error while compiling.")

class SetThreadLimit(Extension):
    def __init__(self, *extensions, config=None):
        super(SetThreadLimit, self).__init__(*extensions, config=config)

    def __call__(self, binary_command, *args, **kwargs):
        from benchbuild.settings import CFG

        config = self.config
        if config is not None and 'jobs' in config.keys():
            jobs = config['jobs']
        else:
            logging.warning("Parameter 'config' was unusable, using defaults")
            jobs = CFG["jobs"].value()

        ret = None
        with local.env(OMP_NUM_THREADS=str(jobs)):
            ret = self.call_next(binary_command, *args, **kwargs)
        return ret
