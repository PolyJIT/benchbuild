"""
Extension base-classes for compile-time and run-time experiments.
"""
import itertools
import logging
from abc import ABCMeta, abstractmethod
from collections import Iterable
from plumbum import local

from benchbuild.utils.run import track_execution, handle_stdin
from benchbuild.utils.db import persist_config, persist_time
from benchbuild.utils.run import fetch_time_output

LOG = logging.getLogger()


class Extension(metaclass=ABCMeta):
    def __init__(self, *extensions):
        self.next_extensions = extensions

    def call_next(self, *args, **kwargs):
        all_results = []
        for ext in self.next_extensions:
            LOG.debug(":: Invoking - {}".format(ext.__class__))
            result = ext(*args, **kwargs)
            LOG.debug(":: Completed - {}".format(ext.__class__))
            LOG.debug(":: Got - {}".format(result))
            if result is None:
                LOG.warning(":: No return from: {}".format(ext.__class__))
                continue
            if isinstance(result, Iterable):
                all_results.extend(result)
            else:
                all_results.append(result)
        return all_results

    def print(self, indent=0):
        LOG.info("{}:: {}".format(indent * " ", self.__class__))
        for ext in self.next_extensions:
            ext.print(indent=indent+2)

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Must provide implementation in subclass")


class RuntimeExtension(Extension):
    def __init__(self, project, experiment, config, *extensions):
        self.config = config
        self.project = project
        self.experiment = experiment

        super(RuntimeExtension, self).__init__(*extensions)

    def __call__(self, binary_command, *args, **kwargs):
        self.project.name = kwargs.get("project_name", self.project.name)

        res = self.call_next(binary_command, *args, **kwargs)

        cmd = handle_stdin(binary_command, kwargs)
        with track_execution(cmd, self.project,
                             self.experiment, **kwargs) as run:
            run_info = run()
            if self.config:
                persist_config(run_info.db_run, run_info.session, self.config)
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
        if not self.next_extensions:
            return None

        res = self.call_next(*args, **kwargs)

        for ext in self.next_extensions:
            if issubclass(LogTrackingMixin, ext.__class__):
                for log in ext.logs:
                    print(log)

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
            for run_info in run_infos:
                if may_wrap:
                    timings = fetch_time_output(
                        time_tag,
                        time_tag + "{:g}-{:g}-{:g}",
                        run_info.stderr.split("\n"))
                    if timings:
                        persist_time(run_info.db_run, run_info.session,
                                     timings)
                    else:
                        LOG.warning("No timing information found.")
            return run_infos

        res = self.call_next(run_cmd, *args, **kwargs)
        return handle_timing(res)
