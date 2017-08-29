"""
Extension base-classes for compile-time and run-time experiments.
"""
import logging
import yaml
from abc import ABCMeta
from collections import Iterable

import os
import parse
from plumbum import local
from benchbuild.utils.run import (track_execution, fetch_time_output)
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
            LOG.debug("  ++ - %s ", ext.__class__)
            results = ext(*args, **kwargs)
            if results is None:
                LOG.warning("No result from: %s", ext.__class__)
                continue
            result_list = []
            if isinstance(results, Iterable):
                result_list.extend(results)
            else:
                result_list.append(results)
            status_list = [r.db_run.status for r in result_list]
            LOG.debug("  -- %s - %s => %s", str(status_list), ext.__class__, results)

            all_results.extend(result_list)

        return all_results

    def print(self, indent=0):
        """Print a structural view of the registered extensions."""
        LOG.info("%s:: %s", indent * " ", self.__class__)
        for ext in self.next_extensions:
            ext.print(indent=indent+2)

    def __call__(self, *args, **kwargs):
        return self.call_next(*args, **kwargs)


class RuntimeExtension(Extension):
    def __init__(self, project, experiment, *extensions, config=None):
        self.project = project
        self.experiment = experiment

        super(RuntimeExtension, self).__init__(*extensions, config=config)

    def __call__(self, binary_command, *args, **kwargs):
        self.project.name = kwargs.get("project_name", self.project.name)

        cmd = binary_command[args]
        with track_execution(cmd, self.project,
                             self.experiment, **kwargs) as run:
            run_info = run()
            if self.config:
                LOG.info(yaml.dump(self.config,
                                   width=40,
                                   indent=4,
                                   default_flow_style=False))
                self.config['baseline'] = \
                    os.getenv("BB_IS_BASELINE", "False")
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
                LOG.debug("Checking additional log files from: %s", ext)
                for log in ext.logs:
                    LOG.debug("Dumping content of '%s'.", log)
                    cat[log] & FG
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
                LOG.debug("Persisting time for '%s'", run_info)
                if may_wrap:
                    timings = fetch_time_output(
                        time_tag,
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
        from benchbuild.utils.schema import CompileStat, Session
        from benchbuild.utils.db import persist_compilestats
        from benchbuild.settings import CFG

        clang = cc["-mllvm", "-stats"]
        run_config = self.config

        session = Session()
        with track_execution(clang, self.project, self.experiment) as run:
            run_info = run()
            if run_config is not None:
                persist_config(
                    run_info.db_run, session, run_config)

        if run_info.db_run.status == "completed":
            stats = []
            for stat in self.get_compilestats(run_info.stderr):
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
                    LOG.info(" [%s] %s = %s",
                             stat.component, stat.name, stat.value)
                persist_compilestats(run_info.db_run, run_info.session, stats)
            else:
                LOG.info("No compilestats left, after filtering.")
                LOG.warning("  Components: %s", components)
                LOG.warning("  Names:      %s", names)
        else:
            LOG.info("There was an error while compiling.")

        ret = self.call_next(cc, *args, **kwargs)
        ret.append(run_info)
        session.commit()
        return ret


class SetThreadLimit(Extension):
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
