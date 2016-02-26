"""
The 'raw' Experiment.

This experiment is the basic experiment in the pprof study. It simply runs
all projects after compiling it with -O3. The binaries are wrapped
with the time command and results are written to the database.

This forms the baseline numbers for the other experiments.

Measurements
------------

3 Metrics are generated during this experiment:
    time.user_s - The time spent in user space in seconds (aka virtual time)
    time.system_s - The time spent in kernel space in seconds (aka system time)
    time.real_s - The time spent overall in seconds (aka Wall clock)
"""

from pprof.experiment import step, substep, RuntimeExperiment
from plumbum import local
from os import path


def run_with_time(project, experiment, config, jobs, run_f, args, **kwargs):
    """
    Run the given binary wrapped with time.

    Args:
        project: The pprof project that has called us.
        experiment: The pprof experiment which we operate under.
        config: The pprof configuration we are running with.
        jobs: The number of cores we are allowed to use. This may differ
            from the actual amount of available cores, obey it.
            We should enforce this from the outside. However, at the moment we
            do not do this.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::pprof.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
    """
    from pprof.utils import run as r
    from pprof.utils.db import persist_time, persist_config
    from pprof.settings import CFG
    from plumbum.cmd import time

    CFG.update(config)
    project_name = kwargs.get("project_name", project.name)
    timing_tag = "PPROF-TIME: "

    run_cmd = time["-f", timing_tag + "%U-%S-%e", run_f]
    run_cmd = r.handle_stdin(run_cmd[args], kwargs)

    with local.env(OMP_NUM_THREADS=str(jobs)):
        run, session, _, _, stderr = \
            r.guarded_exec(run_cmd, project_name, experiment.name,
                           project.run_uuid)
        timings = r.fetch_time_output(
            timing_tag, timing_tag + "{:g}-{:g}-{:g}", stderr.split("\n"))
        if len(timings) == 0:
            return

    persist_time(run, session, timings)
    persist_config(run, session, {"cores": str(jobs)})


class RawRuntime(RuntimeExperiment):
    """The polyjit experiment."""

    NAME = "raw"

    def run_project(self, p):
        """Compile & Run the experiment with -O3 enabled."""
        from pprof.settings import CFG
        from pprof.utils.run import partial
        llvm_libs = path.join(str(CFG["llvm"]["dir"]), "lib")

        with step("RAW -O3"):
            p.ldflags = ["-L" + llvm_libs]
            p.cflags = ["-O3", "-fno-omit-frame-pointer"]
            with substep("reconf & rebuild"):
                p.download()
                p.configure()
                p.build()
            with substep("run {}".format(p.name)):
                p.run(partial(run_with_time, p, self, CFG, str(CFG["jobs"])))
