#!/usr/bin/env python
# encoding: utf-8
"""
PAPI based experiments.

These types of experiments (papi & papi-std) need to instrument the
project with libpprof support to work.

"""
from pprof.experiment import (Experiment, RuntimeExperiment, step, substep,
                              static_var)
from pprof.project import Project
from pprof.settings import config

from plumbum import local
from os import path


@static_var("experiment", None)
@static_var("project", None)
@static_var("jobs", 0)
@static_var("config", None)
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

    You can (read: should) set the following attributes on this functions to
    further configure its run behavior. These are static args, so make sure you
    use them outside of a threaded environment, bad things may happen.

    Static Args:
        experiment: The experiment instance we run under.
        project: The project instance we run under.
        jobs: The number of tasks we should allow, default 0.
        config: The whole configuration pprof was launched with.

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
    timing_tag = "PPROF-PAPI: "

    run_cmd = time["-f", timing_tag + "%U-%S-%e", run_f]
    run_cmd = r.handle_stdin(run_cmd[args], kwargs)

    run, session, retcode, stdout, stderr = \
        r.guarded_exec(run_cmd, project_name, e.name, p.run_uuid)
    timings = r.fetch_time_output(timing_tag, timing_tag + "{:g}-{:g}-{:g}",
                                  stderr.split("\n"))
    if len(timings) == 0:
        return

    persist_time(run, session, timings)
    persist_config(run, session, {"cores": str(jobs)})


class PapiScopCoverage(RuntimeExperiment):
    """PAPI-based dynamic SCoP coverage measurement."""

    def run(self):
        """Do the postprocessing, after all projects are done."""
        super(PapiScopCoverage, self).run()

        bin_path = path.join(config["llvmdir"], "bin")
        pprof_analyze = local[path.join(bin_path, "pprof-analyze")]

        with local.env(PPROF_EXPERIMENT_ID=str(config["experiment"]),
                       PPROF_EXPERIMENT=self.name,
                       PPROF_USE_DATABASE=1,
                       PPROF_USE_FILE=0,
                       PPROF_USE_CSV=0):
            pprof_analyze()

    def run_project(self, p):
        """
        Create & Run a papi-instrumented version of the project.

        This experiment uses the -jitable flag of libPolyJIT to generate
        dynamic SCoP coverage.
        """
        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("Class: Dynamic, PAPI"):
            p.download()
            p.ldflags = ["-L" + llvm_libs, "-lpjit", "-lpprof", "-lpapi"]

            ld_lib_path = [_f
                           for _f in config["ld_library_path"].split(":")
                           if _f]
            p.ldflags = ["-L" + el for el in ld_lib_path] + p.ldflags
            p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli", "-mllvm", "-jitable", "-mllvm",
                        "-instrument", "-mllvm", "-no-recompilation", "-mllvm",
                        "-polly-detect-keep-going"]
            with substep("reconf & rebuild"):
                with local.env(PPROF_ENABLE=0):
                    p.configure()
                    p.build()
            with substep("run"):
                run_with_time.config = config
                run_with_time.experiment = self
                run_with_time.project = p
                run_with_time.jobs = 1

                p.run(run_with_time)

        with step("Evaluation"):
            bin_path = path.join(config["llvmdir"], "bin")
            pprof_calibrate = local[path.join(bin_path, "pprof-calibrate")]
            papi_calibration = self.get_papi_calibration(p, pprof_calibrate)

            self.persist_calibration(p, pprof_calibrate, papi_calibration)


class PapiStandardScopCoverage(PapiScopCoverage):
    """PAPI Scop Coverage, without JIT."""

    def run_project(self, p):
        """
        Create & Run a papi-instrumented version of the project.

        This experiment does not use the -jitable flag of libPolyJIT.
        Therefore, we get the static (aka Standard) SCoP coverage.
        """
        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("Class: Standard - PAPI"):
            p.download()
            p.ldflags = ["-L" + llvm_libs, "-lpjit", "-lpprof", "-lpapi"]

            ld_lib_path = [_f
                           for _f in config["ld_library_path"].split(":")
                           if _f]
            p.ldflags = ["-L" + el for el in ld_lib_path] + p.ldflags
            p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli", "-mllvm", "-instrument", "-mllvm",
                        "-no-recompilation", "-mllvm",
                        "-polly-detect-keep-going"]
            with substep("reconf & rebuild"):
                with local.env(PPROF_ENABLE=0):
                    p.configure()
                    p.build()
            with substep("run"):
                run_with_time.config = config
                run_with_time.experiment = self
                run_with_time.project = p
                run_with_time.jobs = 1

                p.run(run_with_time)

        with step("Evaluation"):
            bin_path = path.join(config["llvmdir"], "bin")
            pprof_calibrate = local[path.join(bin_path, "pprof-calibrate")]
            papi_calibration = self.get_papi_calibration(p, pprof_calibrate)
            self.persist_calibration(p, pprof_calibrate, papi_calibration)
