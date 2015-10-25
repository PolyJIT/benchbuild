#!/usr/bin/env python
# encoding: utf-8
"""
The 'polyjit' experiment.

This experiment uses likwid to measure the performance of all binaries
when running with polyjit support enabled.
"""
from pprof.experiments.compilestats import get_compilestats
from pprof.experiment import step, substep, static_var, RuntimeExperiment
from pprof.project import Project
from pprof.experiment import Experiment
from pprof.settings import config
from pprof.utils.schema import CompileStat

from plumbum import local
from os import path


@static_var("config", None)
@static_var("experiment", None)
@static_var("project", None)
@static_var("jobs", 0)
def run_with_papi(run_f, args, **kwargs):
    """
    Run the given file with PAPI support.

    This just runs the project as PAPI support should be compiled in
    already. If not, this won't do a lot.

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
    from pprof.utils.db import persist_config
    from pprof.settings import config

    p = run_with_papi.project
    e = run_with_papi.experiment
    c = run_with_papi.config
    jobs = run_with_papi.jobs

    config.update(c)

    assert p is not None, "run_with_likwid.project attribute is None."
    assert e is not None, "run_with_likwid.experiment attribute is None."
    assert c is not None, "run_with_likwid.config attribute is None."
    assert isinstance(p, Project), "Wrong type: %r Want: Project" % p
    assert isinstance(e, Experiment), "Wrong type: %r Want: Experiment" % e
    assert isinstance(c, dict), "Wrong type: %r Want: Experiment" % e

    project_name = kwargs.get("project_name", p.name)

    run_cmd = local[run_f]
    run_cmd = r.handle_stdin(run_cmd[args], kwargs)

    with local.env(POLLI_ENABLE_PAPI=1, OMP_NUM_THREADS=jobs):
        run, session, _, _, _ = \
            r.guarded_exec(run_cmd, project_name, e.name, p.run_uuid)

    persist_config(run, session, {
        "cores": str(jobs)
    })


@static_var("config", None)
@static_var("experiment", None)
@static_var("project", None)
@static_var("jobs", 0)
def run_with_likwid(run_f, args, **kwargs):
    """
    Run the given file wrapped by likwid.

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
    from pprof.utils.db import persist_likwid, persist_config
    from pprof.likwid import get_likwid_perfctr
    from pprof.settings import config
    from plumbum.cmd import rm

    p = run_with_likwid.project
    e = run_with_likwid.experiment
    c = run_with_likwid.config
    jobs = run_with_likwid.jobs

    config.update(c)

    assert p is not None, "run_with_likwid.project attribute is None."
    assert e is not None, "run_with_likwid.experiment attribute is None."
    assert c is not None, "run_with_likwid.config attribute is None."
    assert isinstance(p, Project), "Wrong type: %r Want: Project" % p
    assert isinstance(e, Experiment), "Wrong type: %r Want: Experiment" % e
    assert isinstance(c, dict), "Wrong type: %r Want: Experiment" % e

    project_name = kwargs.get("project_name", p.name)
    likwid_f = project_name + ".txt"

    for group in ["CLOCK"]:
        likwid_path = path.join(c["likwiddir"], "bin")
        likwid_perfctr = local[
            path.join(likwid_path, "likwid-perfctr")]
        run_cmd = \
            likwid_perfctr["-O", "-o", likwid_f, "-m",
                           "-C", "0-{:d}".format(jobs),
                           "-g", group, run_f]
        run_cmd = r.handle_stdin(run_cmd[args], kwargs)

        with local.env(POLLI_ENABLE_LIKWID=1):
            run, session, _, _, _ = \
                r.guarded_exec(run_cmd, project_name, e.name, p.run_uuid)

        likwid_measurement = get_likwid_perfctr(likwid_f)
        """ Use the project_name from the binary, because we
            might encounter dynamically generated projects.
        """
        persist_likwid(run, session, likwid_measurement)
        persist_config(run, session, {
            "cores": str(jobs),
            "likwid.group": group
        })
        rm("-f", likwid_f)


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

    assert p is not None, "run_with_likwid.project attribute is None."
    assert e is not None, "run_with_likwid.experiment attribute is None."
    assert c is not None, "run_with_likwid.config attribute is None."
    assert isinstance(p, Project), "Wrong type: %r Want: Project" % p
    assert isinstance(e, Experiment), "Wrong type: %r Want: Experiment" % e
    assert isinstance(c, dict), "Wrong type: %r Want: dict" % c

    project_name = kwargs.get("project_name", p.name)
    timing_tag = "PPROF-JIT: "

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


@static_var("config", None)
@static_var("experiment", None)
@static_var("project", None)
@static_var("jobs", 0)
def run_with_perf(run_f, args, **kwargs):
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
    from pprof.utils.db import persist_perf, persist_config
    from plumbum.cmd import perf
    from plumbum import FG, local
    from os import path

    p = run_with_perf.project
    e = run_with_perf.experiment
    c = run_with_perf.config
    jobs = run_with_perf.jobs

    config.update(c)

    assert p is not None, "run_with_likwid.project attribute is None."
    assert e is not None, "run_with_likwid.experiment attribute is None."
    assert c is not None, "run_with_likwid.config attribute is None."
    assert isinstance(p, Project), "Wrong type: %r Want: Project" % p
    assert isinstance(e, Experiment), "Wrong type: %r Want: Experiment" % e
    assert isinstance(c, dict), "Wrong type: %r Want: dict" % c

    project_name = kwargs.get("project_name", p.name)
    run_cmd = local[run_f]
    run_cmd = r.handle_stdin(run_cmd[args], kwargs)
    run_cmd = perf["record", "-q", "-F", 6249, "-g", run_cmd]

    with local.env(OMP_NUM_THREADS=str(jobs)):
        run_cmd & FG
        run, session, _, _, stderr = \
            r.guarded_exec(local["/bin/true"], project_name, e.name,
                           p.run_uuid)

        fg_path = path.join(config["sourcedir"], "extern/FlameGraph")
        if path.exists(fg_path):
            sc_perf = local[path.join(fg_path, "stackcollapse-perf.pl")]
            flamegraph = local[path.join(fg_path, "flamegraph.pl")]

            fold_cmd = ((perf["script"] | sc_perf) > run_f + ".folded")
            graph_cmd = (flamegraph[run_f + ".folded"] > run_f + ".svg")

            fold_cmd & FG
            graph_cmd & FG
            persist_perf(run, session, run_f + ".svg")
            persist_config(run, session, {
                "cores": str(jobs)
            })


class PolyJIT(RuntimeExperiment):

    """The polyjit experiment."""

    def init_project(self, p):
        """
        Execute the pprof experiment.

        We perform this experiment in 2 steps:
            1. with likwid disabled.
            2. with likwid enabled.
        """
        p.ldflags = ["-lpjit", "-lgomp"]

        ld_lib_path = filter(None, config["ld_library_path"].split(":"))
        p.ldflags = ["-L" + el for el in ld_lib_path] + p.ldflags
        p.cflags = ["-Rpass=\"polyjit*\"",
                    "-Xclang", "-load",
                    "-Xclang", "LLVMPolyJIT.so",
                    "-O3",
                    "-mllvm", "-jitable",
                    "-mllvm", "-polly-only-scop-detection",
                    "-mllvm", "-polly-delinearize=false",
                    "-mllvm", "-polly-detect-keep-going",
                    "-mllvm", "-polli"]
        return p

    def run_project(self, p):
        pass


class PJITRaw(PolyJIT):
    """
        An experiment that executes all projects with PolyJIT support.

        This is our default experiment for speedup measurements.
    """

    def run_project(self, p):
        p = self.init_project(p)
        with local.env(PPROF_ENABLE=0):
            """Run the experiment without likwid."""
            from uuid import uuid4

            p.cflags += ["-fno-omit-frame-pointer"]

            for i in range(1, int(config["jobs"]) + 1):
                p.run_uuid = uuid4()
                with step("time: {} cores & uuid {}".format(i, p.run_uuid)):
                    p.clean()
                    p.prepare()
                    p.download()
                    p.configure()
                    p.build()

                    run_with_time.config = config
                    run_with_time.experiment = self
                    run_with_time.project = p
                    run_with_time.jobs = i
                    p.run(run_with_time)


class PJITperf(PolyJIT):
    """
        An experiment that uses linux perf tools to generate flamegraphs.
    """

    def run_project(self, p):
        p = self.init_project(p)
        with local.env(PPROF_ENABLE=0):
            """Run the experiment without likwid."""
            from uuid import uuid4

            p.cflags += ["-fno-omit-frame-pointer"]
            for i in range(1, int(config["jobs"]) + 1):
                p.run_uuid = uuid4()
                with step("perf: {} cores & uuid {}".format(i, p.run_uuid)):
                    p.clean()
                    p.prepare()
                    p.download()
                    p.configure()
                    p.build()

                    run_with_perf.config = config
                    run_with_perf.experiment = self
                    run_with_perf.project = p
                    run_with_perf.jobs = i
                    p.run(run_with_perf)


class PJITlikwid(PolyJIT):
    """
        An experiment that uses likwid's instrumentation API for profiling.

        This instruments all projects with likwid instrumentation API calls
        in key regions of the JIT.

        This allows for arbitrary profiling of PolyJIT's overhead and run-time
    """

    def run_project(self, p):
        p = self.init_project(p)
        with local.env(PPROF_ENABLE=0):
            """Run the experiment with likwid."""
            from uuid import uuid4

            p.cflags = ["-DLIKWID_PERFMON"] + p.cflags

            for i in range(1, int(config["jobs"]) + 1):
                with step("{} cores & uuid {}".format(i, p.run_uuid)):
                    p.clean()
                    p.prepare()
                    p.download()
                    p.configure()
                    p.build()

                    p.run_uuid = uuid4()
                    run_with_likwid.config = config
                    run_with_likwid.experiment = self
                    run_with_likwid.project = p
                    run_with_likwid.jobs = i
                    p.run(run_with_likwid)


class PJITcs(PolyJIT):
    """
        A simple compile-stats based experiment.

        This enables PolyJIT during the compilation of the project and
        extracts all stats from LLVM's -stats output.
    """

    def run_project(self, p):
        p = self.init_project(p)
        with local.env(PPROF_ENABLE=0):
            """ Compile the project and track the compilestats. """
            from uuid import uuid4

            p.clean()
            p.prepare()
            p.download()
            with substep("Configure Project"):
                def track_compilestats(cc, **kwargs):
                    from pprof.utils import run as r
                    from pprof.utils.db import persist_compilestats
                    from pprof.utils.run import handle_stdin

                    new_cc = handle_stdin(cc["-mllvm", "-stats"], kwargs)

                    run, session, retcode, _, stderr = \
                        r.guarded_exec(new_cc, p.name, self.name, p.run_uuid)

                    if retcode == 0:
                        stats = []
                        for stat in get_compilestats(stderr):
                            c = CompileStat()
                            c.name = stat["desc"].rstrip()
                            c.component = stat["component"].rstrip()
                            c.value = stat["value"]
                            stats.append(c)
                        persist_compilestats(run, session, stats)

                p.run_uuid = uuid4()
                p.compiler_extension = track_compilestats
                p.configure()

        with substep("Build Project"):
            p.build()


class PJITpapi(PolyJIT):
    """
        Experiment that uses PolyJIT's instrumentation facilities.

        This uses PolyJIT to instrument all projects with libPAPI based
        region measurements. In the end the region measurements are
        aggregated and metrics like the dynamic SCoP coverage are extracted.

        This uses the same set of flags as all other PolyJIT based experiments.
    """

    def run(self):
        """Do the postprocessing, after all projects are done."""
        super(PJITpapi, self).run()

        bin_path = path.join(config["llvmdir"], "bin")
        pprof_analyze = local[path.join(bin_path, "pprof-analyze")]

        with local.env(PPROF_EXPERIMENT_ID=str(config["experiment"]),
                       PPROF_EXPERIMENT=self.name,
                       PPROF_USE_DATABASE=1,
                       PPROF_USE_FILE=0,
                       PPROF_USE_CSV=0):
            pprof_analyze()

    def run_project(self, p):
        p = self.init_project(p)
        with local.env(PPROF_ENABLE=1):
            """Run the experiment with papi support."""
            from uuid import uuid4

            p.cflags = ["-mllvm", "-instrument"] + p.cflags
            p.ldflags = p.ldflags + ["-lpprof"]

            for i in range(1, int(config["jobs"]) + 1):
                with step("{} cores & uuid {}".format(i, p.run_uuid)):
                    p.clean()
                    p.prepare()
                    p.download()
                    p.configure()
                    p.build()

                    p.run_uuid = uuid4()
                    run_with_papi.config = config
                    run_with_papi.experiment = self
                    run_with_papi.project = p
                    run_with_papi.jobs = i
                    p.run(run_with_papi)
