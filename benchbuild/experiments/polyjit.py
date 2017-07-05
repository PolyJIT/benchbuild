"""
The 'polyjit' experiment.

This experiment uses likwid to measure the performance of all binaries
when running with polyjit support enabled.
"""
import copy
import glob
import logging
import uuid
from abc import abstractmethod
from functools import partial
import os

from plumbum import local

import benchbuild.extensions as ext
from benchbuild.utils.actions import (Any, RequireAll)
from benchbuild.experiment import RuntimeExperiment
from benchbuild.utils.dict import ExtensibleDict, extend_as_list


LOG = logging.getLogger(__name__)


class PolyJITConfig(object):
    __config = ExtensibleDict(extend_as_list)

    @property
    def argv(self):
        return PolyJITConfig.__config

    def value_to_str(self, key):
        if key not in self.argv:
            return ""
        value = self.argv[key]
        if isinstance(value, list):
            value = " ".join(value)
        LOG.debug("Constructed: {0}={1}".format(key, value))
        return value


class EnablePolyJIT(PolyJITConfig, ext.Extension):
    def __call__(self, binary_command, *args, **kwargs):
        with local.env(PJIT_ARGS=self.value_to_str('PJIT_ARGS')):
            ret = self.call_next(binary_command, *args, **kwargs)
        return ret


class DisablePolyJIT(PolyJITConfig, ext.Extension):
    def __call__(self, binary_command, *args, **kwargs):
        ret = None
        with self.argv(PJIT_ARGS="-pjit-no-specialization"):
            with local.env(PJIT_ARGS=self.value_to_str('PJIT_ARGS')):
                ret = self.call_next(binary_command, *args, **kwargs)
        return ret


class RegisterPolyJITLogs(PolyJITConfig, ext.LogTrackingMixin, ext.Extension):
    def __call__(self, *args, **kwargs):
        """Redirect to RunWithTime, but register additional logs."""
        with self.argv(PJIT_ARGS="-polli-enable-log"):
            ret = self.call_next(*args, **kwargs)
        curdir = os.path.realpath(os.path.curdir)
        files = glob.glob(os.path.join(curdir, "polyjit.*.log"))

        for file in files:
            self.add_log(file)

        return ret

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
    from benchbuild.settings import CFG
    from benchbuild.utils.run import track_execution, handle_stdin
    from benchbuild.utils.db import persist_config

    CFG.update(config)
    project.name = kwargs.get("project_name", project.name)
    run_cmd = local[run_f]
    run_cmd = handle_stdin(run_cmd[args], kwargs)

    with local.env(OMP_NUM_THREADS=jobs):
        with track_execution(run_cmd, project, experiment) as run:
            run_info = run()

    persist_config(run_info.db_run, run_info.session,
                   {"cores": str(jobs)})

class RunWithLikwid(ext.RuntimeExtension):
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

    def __call__(self, binary_command, *args, may_wrap=True, **kwargs):
        from benchbuild.settings import CFG
        from benchbuild.utils.db import persist_likwid, persist_config
        from benchbuild.likwid import get_likwid_perfctr
        from benchbuild.utils.cmd import rm

        self.project.name = kwargs.get("project_name", self.project.name)

        likwid_f = self.project.name + ".txt"
        likwid_path = os.path.join(CFG["likwiddir"], "bin")
        likwid_perfctr = local[os.path.join(likwid_path, "likwid-perfctr")]

        jobs = self.config['jobs']
        for group in ["CLOCK"]:
            run_cmd = \
                likwid_perfctr["-O", "-o", likwid_f, "-m",
                               "-C", "0-{0:d}".format(jobs),
                               "-g", group, binary_command]

            res = []
            with local.env(POLLI_ENABLE_LIKWID=1):
                res = self.call_next(run_cmd, *args, **kwargs)

            likwid_measurement = get_likwid_perfctr(likwid_f)
            for run_info in res:
                persist_likwid(run_info.db_run, run_info.session, likwid_measurement)
                persist_config(run_info.db_run, run_info.session, {
                    "cores": str(jobs),
                    "likwid.group": group
                })
            rm("-f", likwid_f)



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
    from benchbuild.settings import CFG
    from benchbuild.utils.run import track_execution, handle_stdin
    from benchbuild.utils.db import persist_perf, persist_config
    from benchbuild.utils.cmd import perf

    CFG.update(config)
    project.name = kwargs.get("project_name", project.name)
    run_cmd = local[run_f]
    run_cmd = handle_stdin(run_cmd[args], kwargs)
    run_cmd = perf["record", "-q", "-F", 6249, "-g", run_cmd]

    with local.env(OMP_NUM_THREADS=str(jobs)):
        with track_execution(run_cmd, project, experiment) as run:
            ri = run(retcode=None)

        fg_path = os.path.join(CFG["src_dir"], "extern/FlameGraph")
        if os.path.exists(fg_path):
            sc_perf = local[os.path.join(fg_path, "stackcollapse-perf.pl")]
            flamegraph = local[os.path.join(fg_path, "flamegraph.pl")]

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
                          "-O3",
                          "-mllvm", "-polli-allow-modref-calls",
                          "-mllvm", "-polli"]
        return project

    @abstractmethod
    def actions_for_project(self, project):
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
        rawp.runtime_extension = \
            ext.RunWithTime(
                ext.SetThreadLimit(
                    ext.RuntimeExtension(rawp, self, config={"jobs": 1}),
                    config={"jobs": 1}))
        actns.append(RequireAll(self.default_runtime_actions(rawp)))

        pollyp = copy.deepcopy(p)
        pollyp.run_uuid = uuid.uuid4()
        pollyp.cflags = ["-Xclang", "-load",
                         "-Xclang", "LLVMPolly.so",
                         "-mllvm", "-polly", "-mllvm", "-polly-parallel"]
        pollyp.runtime_extension = \
            ext.RunWithTime(
                ext.SetThreadLimit(
                    ext.RuntimeExtension(pollyp, self, config={"jobs": 1}),
                    config={"jobs": 1}))
        actns.append(RequireAll(self.default_runtime_actions(pollyp)))

        jitp = copy.deepcopy(p)
        jitp = PolyJIT.init_project(jitp)
        norecomp = copy.deepcopy(jitp)
        norecomp.cflags += ["-mllvm", "-no-recompilation"]

        for i in range(2, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(norecomp)
            cp.run_uuid = uuid.uuid4()
            cfg = {
                "jobs": i,
                "cores": str(i-1),
                "cores-config": str(i),
                "recompilation": "disabled"
            }

            cp.runtime_extension = \
                ext.LogAdditionals(
                    RegisterPolyJITLogs(
                        ext.RunWithTime(
                            DisablePolyJIT(
                                ext.SetThreadLimit(
                                    ext.RuntimeExtension(cp, self, config=cfg),
                                    config=cfg
                                )))))
            actns.append(RequireAll(self.default_runtime_actions(cp)))

        for i in range(2, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(jitp)
            cp.run_uuid = uuid.uuid4()
            cfg = {
                "jobs": i,
                "cores": str(i-1),
                "cores-config": str(i),
                "recompilation": "enabled"
            }
            cp.runtime_extension = \
                ext.LogAdditionals(
                    RegisterPolyJITLogs(
                        ext.RunWithTime(
                            EnablePolyJIT(
                                ext.SetThreadLimit(
                                    ext.RuntimeExtension(cp, self, config=cfg),
                                    config=cfg
                                )))))
            actns.append(RequireAll(self.default_runtime_actions(cp)))

        return [Any(actns)]


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
            cp.runtime_extension = \
                ext.LogAdditionals(
                    RegisterPolyJITLogs(
                        ext.RunWithTime(
                            EnablePolyJIT(
                                ext.RuntimeExtension(p, self, config={
                                    "jobs": i,
                                    "cores": str(i-1),
                                    "cores-config": str(i),
                                    "recompilation": "enabled"})))))

            actns.extend(self.default_runtime_actions(cp))
        return actns


class PJITperf(PolyJIT):
    """An experiment that uses linux perf tools to generate flamegraphs."""

    NAME = "pj-perf"

    def actions_for_project(self, p):
        from benchbuild.settings import CFG

        p = PolyJIT.init_project(p)

        actns = []
        for i in range(1, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(p)
            cp.run_uuid = uuid.uuid4()
            cp.runtime_extension = partial(run_with_perf, cp, self, CFG, i)
            actns.extend(self.default_runtime_actions(cp))
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
            cp.runtime_extension = \
                RunWithLikwid(
                    cp, self,
                    ext.RuntimeExtension(cp, self, config={'jobs': i}),
                    config={'jobs': i})

            actns.append(RequireAll(self.default_runtime_actions(cp)))
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
        from benchbuild.utils.run import track_execution

        def _track_compilestats(project, experiment, config, clang,
                                **kwargs):
            """Compile the project and track the compilestats."""
            from benchbuild.settings import CFG
            from benchbuild.utils.run import handle_stdin

            CFG.update(config)
            clang = handle_stdin(clang["-mllvm", "-polli-collect-modules"],
                                 kwargs)
            with track_execution(clang, project, experiment) as run:
                run()

        p = PolyJIT.init_project(p)
        p.cflags = ["-DLIKWID_PERFMON"] + p.cflags
        p.compiler_extension = partial(_track_compilestats, p, self, CFG)
        return self.default_compiletime_actions(p)


class Compilestats(PolyJIT):
    """Gather compilestats, with enabled JIT."""

    NAME = "pj-cs"

    def actions_for_project(self, p):
        p = PolyJIT.init_project(p)
        p.compiler_extension = ext.ExtractCompileStats(p, self)
        return self.default_compiletime_actions(p)


class PJITpapi(PolyJIT):
    """
    Experiment that uses PolyJIT's instrumentation facilities.

    This uses PolyJIT to instrument all projects with libPAPI based
    region measurements. In the end the region measurements are
    aggregated and metrics like the dynamic SCoP coverage are extracted.

    This uses the same set of flags as all other PolyJIT based experiments.
    """

    NAME = "pj-papi"

    def actions(self):
        """Do the postprocessing, after all projects are done."""
        actions = super(PJITpapi, self).actions()
        from benchbuild.utils.actions import Step

        class Analyze(Step):
            NAME = "ANALYZE"
            DESCRIPTION = "Analyze the experiment after completion."

        def run_pprof_analyze():
            from benchbuild.settings import CFG
            from benchbuild.utils.cmd import pprof_analyze

            with local.env(BB_EXPERIMENT_ID=str(CFG["experiment_id"]),
                           BB_EXPERIMENT=self.name,
                           BB_USE_DATABASE=1,
                           BB_USE_FILE=0,
                           BB_USE_CSV=0):
                pprof_analyze()

        actions.append(
            Analyze(self, run_pprof_analyze)
        )

        return actions

    def actions_for_project(self, p):
        from benchbuild.settings import CFG

        p = PolyJIT.init_project(p)
        p.cflags = ["-mllvm", "-instrument"] + p.cflags
        p.ldflags = p.ldflags + ["-lpprof"]

        actns = []
        for i in range(1, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(p)
            cp.compiler_extension = ext.ExtractCompileStats(cp, self)
            cp.runtime_extension = partial(run_with_papi, p, self, CFG, i)
            actns.extend(self.default_runtime_actions(cp))

        return actns
