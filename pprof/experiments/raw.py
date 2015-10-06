#!/usr/bin/env python
# encoding: utf-8
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

from pprof.experiment import step, substep, static_var, RuntimeExperiment
from pprof.settings import config
from pprof.project import Project
from pprof.experiment import Experiment

from plumbum import local
from os import path


@static_var("config", None)
@static_var("experiment", None)
@static_var("project", None)
@static_var("jobs", 0)
def run_with_time(run_f, args, **kwargs):
    """
    Run the given binary wrapped with time.

    Args:
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
    from plumbum.cmd import time

    p = run_with_time.project
    e = run_with_time.experiment
    c = run_with_time.config
    jobs = run_with_time.jobs

    config.update(c)

    assert p is not None, "run_with_time.project attribute is None."
    assert e is not None, "run_with_time.experiment attribute is None."
    assert c is not None, "run_with_time.config attribute is None."
    assert isinstance(p, Project), "Wrong type: %r Want: Project" % p
    assert isinstance(e, Experiment), "Wrong type: %r Want: Experiment" % e
    assert isinstance(c, dict), "Wrong type: %r Want: dict" % c

    project_name = kwargs.get("project_name", p.name)
    timing_tag = "PPROF-TIME: "

    run_cmd = time["-f", timing_tag + "%U-%S-%e", run_f]
    run_cmd = r.handle_stdin(run_cmd[args], kwargs)

    with local.env(OMP_NUM_THREADS=str(jobs)):
        run, session, _, _, stderr = \
            r.guarded_exec(run_cmd, project_name, e.name, p.run_uuid)
        timings = r.fetch_time_output(
            timing_tag, timing_tag + "{:g}-{:g}-{:g}",
            stderr.split("\n"))
        if len(timings) == 0:
            return

    persist_time(run, session, timings)
    persist_config(run, session, {
        "cores": str(jobs)
    })


class RawRuntime(RuntimeExperiment):

    """The polyjit experiment."""

    def run_project(self, p):
        """Compile & Run the experiment with -O3 enabled."""
        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("RAW -O3"):
            p.ldflags = ["-L" + llvm_libs]
            p.cflags = ["-O3", "-fno-omit-frame-pointer"]
            with substep("reconf & rebuild"):
                p.download()
                p.configure()
                p.build()
            with substep("run {}".format(p.name)):
                run_with_time.config = config
                run_with_time.experiment = self
                run_with_time.project = p
                run_with_time.jobs = config["jobs"]
                p.run(run_with_time)
