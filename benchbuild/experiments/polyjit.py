"""
The 'polyjit' experiment.

This experiment uses likwid to measure the performance of all binaries
when running with polyjit support enabled.
"""
from abc import abstractmethod
from os import path
import copy
import uuid

from benchbuild.utils.cmd import rm, time  # pylint: disable=E0401
from plumbum import local
from benchbuild.experiments.compilestats import collect_compilestats
from benchbuild.utils.actions import (RequireAll, Prepare, Build, Download,
                                      Configure, Clean, MakeBuildDir, Run,
                                      Echo, Any)
from benchbuild.experiment import RuntimeExperiment
from functools import partial


def run_raw(project, experiment, config, run_f, args, **kwargs):
    """
    Run the given binary wrapped with nothing.

    Args:
        project: The benchbuild.project.
        experiment: The benchbuild.experiment.
        config: The benchbuild.settings.config.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::benchbuild.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
    """
    from benchbuild.utils.run import guarded_exec
    from benchbuild.utils.run import handle_stdin
    from benchbuild.settings import CFG as c

    c.update(config)
    project.name = kwargs.get("project_name", project.name)

    run_cmd = local[run_f]
    run_cmd = handle_stdin(run_cmd[args], kwargs)
    with guarded_exec(run_cmd, project, experiment) as run:
        run()


def run_with_papi(project, experiment, config, jobs, run_f, args, **kwargs):
    """
    Run the given file with PAPI support.

    This just runs the project as PAPI support should be compiled in
    already. If not, this won't do a lot.

    Args:
        project: The benchbuild.project.
        experiment: The benchbuild.experiment.
        config: The benchbuild.settings.config.
        jobs: Number of cores we should use for this exection.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::benchbuild.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
    """
    from benchbuild.settings import CFG as c
    from benchbuild.utils.run import guarded_exec, handle_stdin
    from benchbuild.utils.db import persist_config

    c.update(config)
    project.name = kwargs.get("project_name", project.name)
    run_cmd = local[run_f]
    run_cmd = handle_stdin(run_cmd[args], kwargs)

    with local.env(POLLI_ENABLE_PAPI=1, OMP_NUM_THREADS=jobs):
        with guarded_exec(run_cmd, project, experiment) as run:
            ri = run()

    persist_config(ri.db_run, ri.session,
                   {"cores": str(jobs)})


def run_with_likwid(project, experiment, config, jobs, run_f, args, **kwargs):
    """
    Run the given file wrapped by likwid.

    Args:
        project: The benchbuild.project.
        experiment: The benchbuild.experiment.
        config: The benchbuild.settings.config.
        jobs: Number of cores we should use for this exection.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::benchbuild.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
    """
    from benchbuild.settings import CFG as c
    from benchbuild.utils.run import guarded_exec, handle_stdin
    from benchbuild.utils.db import persist_likwid, persist_config
    from benchbuild.likwid import get_likwid_perfctr

    c.update(config)
    project.name = kwargs.get("project_name", project.name)
    likwid_f = project.name + ".txt"

    for group in ["CLOCK"]:
        likwid_path = path.join(c["likwiddir"], "bin")
        likwid_perfctr = local[path.join(likwid_path, "likwid-perfctr")]
        run_cmd = \
            likwid_perfctr["-O", "-o", likwid_f, "-m",
                           "-C", "0-{0:d}".format(jobs),
                           "-g", group, run_f]
        run_cmd = handle_stdin(run_cmd[args], kwargs)

        with local.env(POLLI_ENABLE_LIKWID=1):
            with guarded_exec(run_cmd, project, experiment) as run:
                ri = run()

        likwid_measurement = get_likwid_perfctr(likwid_f)
        persist_likwid(run, ri.session, likwid_measurement)
        persist_config(run, ri.session, {
            "cores": str(jobs),
            "likwid.group": group
        })
        rm("-f", likwid_f)


def run_with_time(project, experiment, config, jobs, run_f, args, **kwargs):
    """
    Run the given binary wrapped with time.

    Args:
        project: The benchbuild.project.
        experiment: The benchbuild.experiment.
        config: The benchbuild.settings.config.
        jobs: Number of cores we should use for this exection.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::benchbuild.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
    """
    from benchbuild.utils.run import guarded_exec, handle_stdin, fetch_time_output
    from benchbuild.settings import CFG as c
    from benchbuild.utils.db import persist_time, persist_config

    c.update(config)
    project.name = kwargs.get("project_name", project.name)
    timing_tag = "BB-JIT: "

    may_wrap = kwargs.get("may_wrap", True)

    run_cmd = local[run_f]
    run_cmd = run_cmd[args]
    if may_wrap:
        run_cmd = time["-f", timing_tag + "%U-%S-%e", run_cmd]

    with local.env(OMP_NUM_THREADS=str(jobs),
                   POLLI_LOG_FILE=c["slurm"]["extra_log"].value()):
        with guarded_exec(run_cmd, project, experiment) as run:
            ri = run()

        if may_wrap:
            timings = fetch_time_output(
                timing_tag, timing_tag + "{:g}-{:g}-{:g}", ri.stderr.split("\n"))
            if timings:
                persist_time(ri.db_run, ri.session, timings)
    persist_config(ri.db_run, ri.session, {"cores": str(jobs-1),
                                           "cores-config": str(jobs),
                                           "recompilation": "enabled"})
    return ri


def run_without_recompile(project, experiment, config, jobs, run_f,
                          args, **kwargs):
    """
    Run the given binary wrapped with time.

    Args:
        project: The benchbuild.project.
        experiment: The benchbuild.experiment.
        config: The benchbuild.settings.config.
        jobs: Number of cores we should use for this exection.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::benchbuild.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
    """
    from benchbuild.utils.run import guarded_exec, handle_stdin, fetch_time_output
    from benchbuild.settings import CFG as c
    from benchbuild.utils.db import persist_time, persist_config

    c.update(config)
    project.name = kwargs.get("project_name", project.name)
    timing_tag = "BB-JIT: "

    may_wrap = kwargs.get("may_wrap", True)

    run_cmd = local[run_f]
    run_cmd = run_cmd[args]
    if may_wrap:
        run_cmd = time["-f", timing_tag + "%U-%S-%e", run_cmd]

    with local.env(OMP_NUM_THREADS=str(jobs),
                   POLLI_LOG_FILE=c["slurm"]["extra_log"].value()):
        with guarded_exec(run_cmd, project, experiment) as run:
            ri = run()

        if may_wrap:
            timings = fetch_time_output(
                timing_tag, timing_tag + "{:g}-{:g}-{:g}", ri.stderr.split("\n"))
            if timings:
                persist_time(ri.db_run, ri.session, timings)
    persist_config(ri.db_run, ri.session, {"cores": str(jobs-1),
                                           "cores-config": str(jobs),
                                           "recompilation": "disabled"})
    return ri

def run_with_perf(project, experiment, config, jobs, run_f, args, **kwargs):
    """
    Run the given binary wrapped with time.

    Args:
        project: The benchbuild.project.
        experiment: The benchbuild.experiment.
        config: The benchbuild.settings.config.
        jobs: Number of cores we should use for this exection.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::benchbuild.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
    """
    from benchbuild.settings import CFG as c
    from benchbuild.utils.run import guarded_exec, handle_stdin
    from benchbuild.utils.db import persist_perf, persist_config
    from benchbuild.utils.cmd import perf

    c.update(config)
    project.name = kwargs.get("project_name", project.name)
    run_cmd = local[run_f]
    run_cmd = handle_stdin(run_cmd[args], kwargs)
    run_cmd = perf["record", "-q", "-F", 6249, "-g", run_cmd]

    with local.env(OMP_NUM_THREADS=str(jobs)):
        with guarded_exec(run_cmd, project, experiment) as run:
            ri = run(retcode=None)

        fg_path = path.join(c["src_dir"], "extern/FlameGraph")
        if path.exists(fg_path):
            sc_perf = local[path.join(fg_path, "stackcollapse-perf.pl")]
            flamegraph = local[path.join(fg_path, "flamegraph.pl")]

            fold_cmd = ((perf["script"] | sc_perf) > run_f + ".folded")
            graph_cmd = (flamegraph[run_f + ".folded"] > run_f + ".svg")

            fold_cmd()
            graph_cmd()
            persist_perf(ri.db_run, ri.session, run_f + ".svg")
            persist_config(ri.db_run, ri.session, {"cores": str(jobs)})


class PolyJIT(RuntimeExperiment):
    """The polyjit experiment."""

    @classmethod
    def init_project(cls, project):
        """
        Execute the benchbuild experiment.

        We perform this experiment in 2 steps:
            1. with likwid disabled.
            2. with likwid enabled.

        Args:
            project: The project we initialize.

        Returns:
            The initialized project.
        """
        project.ldflags += ["-lpjit", "-lgomp"]
        project.cflags = ["-fno-omit-frame-pointer",
                          "-rdynamic",
                          "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                          "-O3", "-mllvm", "-jitable",
                          "-mllvm", "-polli-allow-modref-calls",
                          "-mllvm", "-polli"]
        return project

    @abstractmethod
    def actions_for_project(self, p):
        pass


class PolyJITFull(PolyJIT):
    """
        An experiment that executes all projects with PolyJIT support.

        This is our default experiment for speedup measurements.
    """

    NAME = "pj"

    def actions_for_project(self, p):
        from benchbuild.settings import CFG

        p.cflags = ["-O3", "-fno-omit-frame-pointer"]

        actns = []
        rawp = copy.deepcopy(p)
        rawp.run_uuid = uuid.uuid4()
        rawp.runtime_extension = partial(run_with_time, rawp, self, CFG, 1)

        actns.append(RequireAll([
            Echo("========= START: RAW Baseline"),
            MakeBuildDir(rawp),
            Prepare(rawp),
            Download(rawp),
            Configure(rawp),
            Build(rawp),
            Run(rawp),
            Clean(rawp),
            Echo("========= END: RAW Baseline")
        ]))

        jitp = copy.deepcopy(p)
        jitp = PolyJIT.init_project(jitp)
        norecomp = copy.deepcopy(jitp)
        norecomp.cflags += ["-mllvm", "-no-recompilation"]

        for i in range(2, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(norecomp)
            cp.run_uuid = uuid.uuid4()
            cp.runtime_extension = partial(run_without_recompile,
                                           cp, self, CFG, i)

            actns.append(RequireAll([
                Echo("========= START: JIT No Recomp - Cores: {0}".format(i)),
                MakeBuildDir(cp),
                Prepare(cp),
                Download(cp),
                Configure(cp),
                Build(cp),
                Run(cp),
                Clean(cp),
                Echo("========= END: JIT No Recomp - Cores: {0}".format(i))
            ]))

        for i in range(2, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(jitp)
            cp.run_uuid = uuid.uuid4()
            cp.runtime_extension = partial(run_with_time, cp, self, CFG, i)

            actns.append(RequireAll([
                Echo("========= START: JIT - Cores: {0}".format(i)),
                MakeBuildDir(cp),
                Prepare(cp),
                Download(cp),
                Configure(cp),
                Build(cp),
                Run(cp),
                Clean(cp),
                Echo("========= END: JIT - Cores: {0}".format(i))
            ]))
        return [Any(actns)]


class PJIT_Test(PolyJIT):
    """
        An experiment that executes all projects with PolyJIT support.

        This is our default experiment for speedup measurements.
    """

    NAME = "pj-test"

    def actions_for_project(self, p):
        from benchbuild.settings import CFG

        p = PolyJIT.init_project(p)

        actns = []
        p.run_uuid = uuid.uuid4()
        jobs = CFG["jobs"]
        p.cflags += ["-mllvm", "-polly-num-threads={0}".format(jobs)]
        p.runtime_extension = partial(run_with_time, p, self, CFG, jobs)

        actns.extend([
            MakeBuildDir(p),
            Prepare(p),
            Download(p),
            Configure(p),
            Build(p),
            Run(p),
            Clean(p)
        ])
        return actns


class PJITRaw(PolyJIT):
    """
        An experiment that executes all projects with PolyJIT support.

        This is our default experiment for speedup measurements.
    """

    NAME = "pj-raw"

    def actions_for_project(self, p):
        from benchbuild.settings import CFG

        p = PolyJIT.init_project(p)

        actns = []
        for i in range(2, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(p)
            cp.run_uuid = uuid.uuid4()
            cp.cflags += ["-mllvm", "-polly-num-threads={0}".format(i)]
            cp.runtime_extension = partial(run_with_time, cp, self, CFG, i)

            actns.extend([
                MakeBuildDir(cp),
                Echo("{0} core configuration. Configure & Compile".format(i)),
                Prepare(cp),
                Download(cp),
                Configure(cp),
                Build(cp),
                Echo("{0} core configuration. Run".format(i)),
                Run(cp),
                Clean(cp)
            ])
        return actns


class PJITperf(PolyJIT):
    """
        An experiment that uses linux perf tools to generate flamegraphs.
    """

    NAME = "pj-perf"

    def actions_for_project(self, p):
        from benchbuild.settings import CFG

        p = PolyJIT.init_project(p)

        actns = []
        for i in range(1, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(p)
            cp.run_uuid = uuid.uuid4()
            cp.runtime_extension = partial(run_with_perf, cp, self, CFG, i)

            actns.extend([
                MakeBuildDir(cp),
                Echo("perf: {0} core configuration. Configure & Compile".format(i)),
                Prepare(cp),
                Download(cp),
                Configure(cp),
                Build(cp),
                Echo("perf: {0} core configuration. Run".format(i)),
                Run(cp),
                Clean(cp)
            ])
        return actns


class PJITlikwid(PolyJIT):
    """
        An experiment that uses likwid's instrumentation API for profiling.

        This instruments all projects with likwid instrumentation API calls
        in key regions of the JIT.

        This allows for arbitrary profiling of PolyJIT's overhead and run-time
    """

    NAME = "pj-likwid"

    def actions_for_project(self, p):
        from benchbuild.settings import CFG

        p = PolyJIT.init_project(p)
        p.cflags = ["-DLIKWID_PERFMON"] + p.cflags

        actns = []
        for i in range(1, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(p)
            cp.run_uuid = uuid.uuid4()
            cp.runtime_extension = partial(run_with_likwid, cp, self, CFG, i)

            actns.append(RequireAll([
                MakeBuildDir(cp),
                Echo("likwid: {0} core configuration. Configure & Compile".format(i)),
                Prepare(cp),
                Download(cp),
                Configure(cp),
                Build(cp),
                Echo("likwid: {0} core configuration. Run".format(i)),
                Run(cp),
                Clean(cp)]))
        return actns


class PJITRegression(PolyJIT):
    """
        This experiment will generate a series of regression tests.

        This can be used every time a new revision is produced for PolyJIT, as
        it will automatically collect any new SCoPs detected, using the JIT.

        The collection of the tests itself is intgrated into the JIT, so this
        experiment looks a lot like a RAW experiment, except we don't run
        anything.
    """

    NAME = "pj-collect"

    def actions_for_project(self, p):
        from benchbuild.settings import CFG
        from benchbuild.utils.run import guarded_exec

        def _track_compilestats(project, experiment, config, clang,
                                **kwargs):
            """ Compile the project and track the compilestats. """
            from benchbuild.settings import CFG as c
            from benchbuild.utils.run import handle_stdin

            c.update(config)
            clang = handle_stdin(clang["-mllvm", "-polli-collect-modules"],
                                 kwargs)
            with guarded_exec(clang, project, experiment) as run:
                run()

        p = PolyJIT.init_project(p)
        p.cflags = ["-DLIKWID_PERFMON"] + p.cflags
        p.compiler_extension = partial(_track_compilestats, p, self, CFG)

        actns = [
            MakeBuildDir(p),
            Echo("{}: Configure...".format(self.name)),
            Prepare(p),
            Download(p),
            Configure(p),
            Echo("{}: Building...".format(self.name)),
            Build(p),
            Clean(p)
        ]
        return actns


class Compilestats(PolyJIT):
    """Gather compilestats, with enabled JIT."""
    NAME = "pj-cs"

    def actions_for_project(self, p):
        from benchbuild.settings import CFG

        p = PolyJIT.init_project(p)
        p.compiler_extension = partial(collect_compilestats, p, self, CFG)

        actns = [
            MakeBuildDir(p),
            Echo("{}: Configure...".format(self.name)),
            Prepare(p),
            Download(p),
            Configure(p),
            Echo("{}: Building...".format(self.name)),
            Build(p),
            Clean(p)
        ]
        return actns


class PJITpapi(PolyJIT):
    """
        Experiment that uses PolyJIT's instrumentation facilities.

        This uses PolyJIT to instrument all projects with libPAPI based
        region measurements. In the end the region measurements are
        aggregated and metrics like the dynamic SCoP coverage are extracted.

        This uses the same set of flags as all other PolyJIT based experiments.
    """

    NAME = "pj-papi"

    def run(self):
        """Do the postprocessing, after all projects are done."""
        super(PJITpapi, self).run()

        from benchbuild.settings import CFG
        from benchbuild.utils.cmd import pprof_analyze

        with local.env(BB_EXPERIMENT_ID=str(CFG["experiment_id"]),
                       BB_EXPERIMENT=self.name,
                       BB_USE_DATABASE=1,
                       BB_USE_FILE=0,
                       BB_USE_CSV=0):
            pprof_analyze()

    def actions_for_project(self, p):
        from benchbuild.settings import CFG

        p = PolyJIT.init_project(p)
        p.cflags = ["-mllvm", "-instrument"] + p.cflags
        p.ldflags = p.ldflags + ["-lbenchbuild"]

        actns = []
        for i in range(1, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(p)
            cp.compiler_extension = partial(collect_compilestats, cp, self, CFG)
            cp.runtime_extension = partial(run_with_papi, p, self, CFG, i)
            actns.extend([
                MakeBuildDir(cp),
                Echo("{}: Configure...".format(self.name)),
                Prepare(cp),
                Download(cp),
                Configure(cp),
                Echo("{}: Building...".format(self.name)),
                Build(cp),
                Clean(cp)
            ])

        return actns
