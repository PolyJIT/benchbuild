"""
The 'polyjit' experiment.

This experiment uses likwid to measure the performance of all binaries
when running with polyjit support enabled.
"""
from abc import abstractmethod
from os import path
from plumbum.cmd import rm, time  # pylint: disable=E0401
from plumbum import local
from pprof.experiments.compilestats import get_compilestats
from pprof.experiment import step, substep, RuntimeExperiment
from pprof.utils.run import partial


def collect_compilestats(project, experiment, config, clang, **kwargs):
    """Collect compilestats."""
    from pprof.utils import run as r
    from pprof.settings import CFG as c
    from pprof.utils.db import persist_compilestats
    from pprof.utils.run import handle_stdin
    from pprof.utils.schema import CompileStat

    c.update(config)
    clang = handle_stdin(clang["-mllvm", "-stats"], kwargs)

    with local.env(PPROF_ENABLE=0):
        run, session, retcode, _, stderr = \
            r.guarded_exec(clang, project.name, experiment.name, project.run_uuid)

    if retcode == 0:
        stats = []
        for stat in get_compilestats(stderr):
            compile_s = CompileStat()
            compile_s.name = stat["desc"].rstrip()
            compile_s.component = stat["component"].rstrip()
            compile_s.value = stat["value"]
            stats.append(compile_s)
        persist_compilestats(run, session, stats)


def run_raw(project, experiment, config, run_f, args, **kwargs):
    """
    Run the given binary wrapped with nothing.

    Args:
        project: The pprof.project.
        experiment: The pprof.experiment.
        config: The pprof.settings.config.
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
    from pprof.settings import CFG as c

    c.update(config)
    project_name = kwargs.get("project_name", project.name)

    run_cmd = local[run_f]
    run_cmd = r.handle_stdin(run_cmd[args], kwargs)
    r.guarded_exec(run_cmd, project_name, experiment.name, project.run_uuid)


def run_with_papi(project, experiment, config, jobs, run_f, args, **kwargs):
    """
    Run the given file with PAPI support.

    This just runs the project as PAPI support should be compiled in
    already. If not, this won't do a lot.

    Args:
        project: The pprof.project.
        experiment: The pprof.experiment.
        config: The pprof.settings.config.
        jobs: Number of cores we should use for this exection.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::pprof.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
    """
    from pprof.settings import CFG as c
    from pprof.utils import run as r
    from pprof.utils.db import persist_config

    c.update(config)
    project_name = kwargs.get("project_name", project.name)
    run_cmd = local[run_f]
    run_cmd = r.handle_stdin(run_cmd[args], kwargs)

    with local.env(POLLI_ENABLE_PAPI=1, OMP_NUM_THREADS=jobs):
        run, session, _, _, _ = \
            r.guarded_exec(run_cmd, project_name, experiment.name,
                           project.run_uuid)

    persist_config(run, session, {"cores": str(jobs)})


def run_with_likwid(project, experiment, config, jobs, run_f, args, **kwargs):
    """
    Run the given file wrapped by likwid.

    Args:
        project: The pprof.project.
        experiment: The pprof.experiment.
        config: The pprof.settings.config.
        jobs: Number of cores we should use for this exection.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::pprof.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
    """
    from pprof.settings import CFG as c
    from pprof.utils import run as r
    from pprof.utils.db import persist_likwid, persist_config
    from pprof.likwid import get_likwid_perfctr

    c.update(config)
    project_name = kwargs.get("project_name", project.name)
    likwid_f = project_name + ".txt"

    for group in ["CLOCK"]:
        likwid_path = path.join(c["likwiddir"], "bin")
        likwid_perfctr = local[path.join(likwid_path, "likwid-perfctr")]
        run_cmd = \
            likwid_perfctr["-O", "-o", likwid_f, "-m",
                           "-C", "0-{:d}".format(jobs),
                           "-g", group, run_f]
        run_cmd = r.handle_stdin(run_cmd[args], kwargs)

        with local.env(POLLI_ENABLE_LIKWID=1):
            run, session, _, _, _ = \
                r.guarded_exec(run_cmd, project_name, experiment.name,
                               project.run_uuid)

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


def run_with_time(project, experiment, config, jobs, run_f, args, **kwargs):
    """
    Run the given binary wrapped with time.

    Args:
        project: The pprof.project.
        experiment: The pprof.experiment.
        config: The pprof.settings.config.
        jobs: Number of cores we should use for this exection.
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
    from pprof.settings import CFG as c
    from pprof.utils.db import persist_time, persist_config

    c.update(config)
    project_name = kwargs.get("project_name", project.name)
    timing_tag = "PPROF-JIT: "

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


def run_with_perf(project, experiment, config, jobs, run_f, args, **kwargs):
    """
    Run the given binary wrapped with time.

    Args:
        project: The pprof.project.
        experiment: The pprof.experiment.
        config: The pprof.settings.config.
        jobs: Number of cores we should use for this exection.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::pprof.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
    """
    from pprof.settings import CFG as c
    from pprof.utils import run as r
    from pprof.utils.db import persist_perf, persist_config
    from plumbum.cmd import perf

    c.update(config)
    project_name = kwargs.get("project_name", project.name)
    run_cmd = local[run_f]
    run_cmd = r.handle_stdin(run_cmd[args], kwargs)
    run_cmd = perf["record", "-q", "-F", 6249, "-g", run_cmd]

    with local.env(OMP_NUM_THREADS=str(jobs)):
        run_cmd()
        run, session, _, _, _ = \
            r.guarded_exec(local["/bin/true"], project_name, experiment.name,
                           project.run_uuid)

        fg_path = path.join(c["src_dir"], "extern/FlameGraph")
        if path.exists(fg_path):
            sc_perf = local[path.join(fg_path, "stackcollapse-perf.pl")]
            flamegraph = local[path.join(fg_path, "flamegraph.pl")]

            fold_cmd = ((perf["script"] | sc_perf) > run_f + ".folded")
            graph_cmd = (flamegraph[run_f + ".folded"] > run_f + ".svg")

            fold_cmd()
            graph_cmd()
            persist_perf(run, session, run_f + ".svg")
            persist_config(run, session, {"cores": str(jobs)})


class PolyJIT(RuntimeExperiment):
    """The polyjit experiment."""

    def init_project(self, project):
        """
        Execute the pprof experiment.

        We perform this experiment in 2 steps:
            1. with likwid disabled.
            2. with likwid enabled.

        Args:
            project: The project we initialize.

        Returns:
            The initialized project.
        """
        from pprof.settings import CFG
        project.ldflags = ["-lpjit", "-lgomp"]

        ld_lib_path = [_f for _f in str(CFG["ld_library_path"]).split(":") if _f]
        project.ldflags = ["-L" + el for el in ld_lib_path] + project.ldflags
        project.cflags = ["-Rpass=\"polyjit*\"", "-Xclang", "-load", "-Xclang",
                          "LLVMPolyJIT.so", "-O3", "-mllvm", "-jitable",
                          "-mllvm", "-polli-analyze", "-mllvm", "-polli"]
        return project

    @abstractmethod
    def run_project(self, p):
        pass


class PJITRaw(PolyJIT):
    """
        An experiment that executes all projects with PolyJIT support.

        This is our default experiment for speedup measurements.
    """

    NAME = "pj-raw"

    def run_project(self, p):
        from pprof.settings import CFG

        p = self.init_project(p)
        with local.env(PPROF_ENABLE=0):
            from uuid import uuid4

            p.cflags += ["-fno-omit-frame-pointer"]

            for i in range(1, int(str(CFG["jobs"])) + 1):
                p.run_uuid = uuid4()
                with step("time: {} cores & uuid {}".format(i, p.run_uuid)):
                    p.clean()
                    p.prepare()
                    p.download()
                    p.configure()
                    p.build()
                    p.run(partial(run_with_time, p, self, CFG, i))


class PJITperf(PolyJIT):
    """
        An experiment that uses linux perf tools to generate flamegraphs.
    """

    NAME = "pj-perf"

    def run_project(self, p):
        from pprof.settings import CFG
        p = self.init_project(p)
        with local.env(PPROF_ENABLE=0):
            from uuid import uuid4

            p.cflags += ["-fno-omit-frame-pointer"]
            for i in range(1, int(CFG["jobs"]) + 1):
                p.run_uuid = uuid4()
                with step("perf: {} cores & uuid {}".format(i, p.run_uuid)):
                    p.clean()
                    p.prepare()
                    p.download()
                    p.configure()
                    p.build()
                    p.run(partial(run_with_perf, p, self, CFG, i))


class PJITlikwid(PolyJIT):
    """
        An experiment that uses likwid's instrumentation API for profiling.

        This instruments all projects with likwid instrumentation API calls
        in key regions of the JIT.

        This allows for arbitrary profiling of PolyJIT's overhead and run-time
    """

    NAME = "pj-likwid"

    def run_project(self, p):
        from pprof.settings import CFG

        p = self.init_project(p)
        with local.env(PPROF_ENABLE=0):
            from uuid import uuid4

            p.cflags = ["-DLIKWID_PERFMON"] + p.cflags

            for i in range(1, int(CFG["jobs"]) + 1):
                with step("{} cores & uuid {}".format(i, p.run_uuid)):
                    p.clean()
                    p.prepare()
                    p.download()
                    p.configure()
                    p.build()

                    p.run_uuid = uuid4()
                    run_with_likwid.config = CFG
                    run_with_likwid.experiment = self
                    run_with_likwid.project = p
                    run_with_likwid.jobs = i
                    p.run(partial(run_with_likwid, p, self, CFG, i))


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

    def run_project(self, p):
        """
        Execute the experiment on a single projects.

        Args:
            p - The project we run this experiment on.
        """
        from pprof.settings import CFG

        p = self.init_project(p)
        with local.env(PPROF_ENABLE=0):

            def _track_compilestats(project, experiment, config, clang,
                                    **kwargs):
                """ Compile the project and track the compilestats. """
                from pprof.utils import run as r
                from pprof.settings import CFG as c
                from pprof.utils.run import handle_stdin

                c.update(config)
                clang = handle_stdin(clang["-mllvm", "-polli-collect-modules"],
                                     kwargs)
                pname = project.name
                ename = experiment.name
                ruuid = project.run_uuid
                r.guarded_exec(clang, pname, ename, ruuid)

            with step("Extract regression test modules."):
                p.clean()
                p.prepare()
                p.download()
                p.compiler_extension = partial(_track_compilestats, p, self,
                                               CFG)
                p.configure()
                p.build()
                p.run(partial(run_raw, p, self, CFG, 1))


class PolyJIT_CompileStats(PolyJIT):
    """Gather compilestats, with enabled JIT."""
    NAME = "pj-cs"

    def run_project(self, p):
        """ 
        Args:
            p: The project we run.
        """
        from pprof.settings import CFG

        p = self.init_project(p)
        with local.env(PPROF_ENABLE=1):
            from uuid import uuid4

            p.compiler_extension = partial(collect_compilestats, p, self, CFG)
            p.clean()
            p.prepare()
            p.download()
            p.configure()
            p.build()


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

        from pprof.settings import CFG

        bin_path = path.join(str(CFG["llvm"]["dir"]), "bin")
        pprof_analyze = local[path.join(bin_path, "pprof-analyze")]

        with local.env(PPROF_EXPERIMENT_ID=str(CFG["experiment"]),
                       PPROF_EXPERIMENT=self.name,
                       PPROF_USE_DATABASE=1,
                       PPROF_USE_FILE=0,
                       PPROF_USE_CSV=0):
            pprof_analyze()

    def run_project(self, p):
        """
        Run the experiment with papi support.

        Args:
            p: The project we run.
        """
        from pprof.settings import CFG

        p = self.init_project(p)
        with local.env(PPROF_ENABLE=1):
            from uuid import uuid4

            p.cflags = ["-mllvm", "-instrument"] + p.cflags
            p.ldflags = p.ldflags + ["-lpprof"]

            for i in range(1, int(str(CFG["jobs"])) + 1):
                with step("{} cores & uuid {}".format(i, p.run_uuid)):
                    p.clean()
                    p.prepare()
                    p.download()
                    with local.env(PPROF_ENABLE=0):
                        p.compiler_extension = partial(collect_compilestats, p,
                                                       self, CFG)
                        p.configure()
                        p.build()

                    p.run_uuid = uuid4()
                    p.run(partial(run_with_papi, p, self, CFG, i))
