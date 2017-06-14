"""
Extension base-classes for compile-time and run-time experiments.
"""
import logging
from abc import ABCMeta, abstractmethod
from plumbum import local

from benchbuild.utils.run import track_execution, handle_stdin
from benchbuild.utils.db import persist_config, persist_time
from benchbuild.utils.run import fetch_time_output

LOG = logging.getLogger()

class Extension(metaclass=ABCMeta):
    def __init__(self, project, experiment):
        self.project = project
        self.experiment = experiment


class CompilerExtension(Extension):
    @abstractmethod
    def __call__(self, compiler_command,
                 config=None, **kwargs):
        pass


class RuntimeExtension(Extension):
    def __init__(self, project, experiment, config):
        self.config = config
        super(RuntimeExtension, self).__init__(project, experiment)

    @abstractmethod
    def __call__(self, binary_command, *args,
                 config=None, **kwargs):
        self.project.name = kwargs.get("project_name", self.project.name)

        cmd = handle_stdin(binary_command, kwargs)
        with track_execution(cmd, self.project,
                             self.experiment, **kwargs) as run:
            run_info = run()
            if self.config:
                persist_config(run_info.db_run, run_info.session, self.config)
        return run_info


class RunWithTime(RuntimeExtension):
    def __call__(self, binary_command, *args, may_wrap=True, **kwargs):
        from benchbuild.utils.cmd import time
        run_cmd = local[binary_command]
        run_cmd = run_cmd[args]
        time_tag = "BENCHBUILD: "
        if may_wrap:
            run_cmd = time["-f", time_tag + "%U-%S-%e", run_cmd]

        def handle_timing(run_info):
            """Takes care of the formating for the timing statistics."""
            if may_wrap:
                timings = fetch_time_output(
                    time_tag,
                    time_tag + "{:g}-{:g}-{:g}",
                    run_info.stderr.split("\n"))
                if timings:
                    persist_time(run_info.db_run, run_info.session, timings)
                else:
                    LOG.warn("No timing information found.")
            return run_info

        return handle_timing(super(RunWithTime, self).__call__(
            run_cmd, *args, **kwargs))
