"""
PAPI based experiments.

These types of experiments (papi & papi-std) need to instrument the
project with libbenchbuild support to work.

"""
from benchbuild.experiment import RuntimeExperiment
from benchbuild.extensions import (ExtractCompileStats, RunWithTime,
                                   RuntimeExtension)
from benchbuild.utils.actions import Step
from benchbuild.settings import CFG
from plumbum import local


class Calibrate(Step):
    NAME = "CALIBRATE"
    DESCRIPTION = "Calibrate libpapi measurement functions."


class Analyze(Step):
    NAME = "ANALYZE"
    DESCRIPTION = "Analyze the experiment after completion."


class PapiScopCoverage(RuntimeExperiment):
    """PAPI-based dynamic SCoP coverage measurement."""

    NAME = "papi"

    def actions(self):
        """Do the postprocessing, after all projects are done."""
        actions = super(PapiScopCoverage, self).actions()

        def run_pprof_analyze():
            from benchbuild.utils.cmd import pprof_analyze

            with local.env(BB_EXPERIMENT_ID=str(CFG["experiment_id"]),
                           BB_EXPERIMENT=self.name,
                           BB_USE_DATABASE=1,
                           BB_USE_FILE=0,
                           BB_USE_CSV=0):
                pprof_analyze()

        actions.extend([
            Analyze(self, run_pprof_analyze),
        ])

        return actions

    def actions_for_project(self, p):
        """
        Create & Run a papi-instrumented version of the project.

        This experiment uses the -jitable flag of libPolyJIT to generate
        dynamic SCoP coverage.
        """
        p.ldflags = p.ldflags + ["-lpjit", "-lpprof", "-lpapi"]
        p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                    "-mllvm", "-polli", "-mllvm",
                    "-instrument", "-mllvm", "-no-recompilation", "-mllvm",
                    "-polly-detect-keep-going"]
        p.compiler_extension = ExtractCompileStats(p, self)
        p.runtime_extension = \
            RunWithTime(
                RuntimeExtension(p, self, config={'jobs': 1}))

        def evaluate_calibration(e):
            from benchbuild.utils.cmd import pprof_calibrate
            papi_calibration = e.get_papi_calibration(p, pprof_calibrate)
            e.persist_calibration(p, pprof_calibrate, papi_calibration)


        actns = self.default_runtime_actions(p)
        actns.append(Calibrate(self, evaluate_calibration))
        return self.default_runtime_actions(p)


class PapiStandardScopCoverage(PapiScopCoverage):
    """PAPI Scop Coverage, without JIT."""

    NAME = "papi-std"

    def actions_for_project(self, p):
        """
        Create & Run a papi-instrumented version of the project.

        This experiment uses the -jitable flag of libPolyJIT to generate
        dynamic SCoP coverage.
        """
        p.ldflags = p.ldflags + ["-lpjit", "-lbenchbuild", "-lpapi"]
        p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                    "-mllvm", "-polli", "-mllvm", "-instrument", "-mllvm",
                    "-no-recompilation", "-mllvm",
                    "-polly-detect-keep-going"]
        p.compiler_extension = ExtractCompileStats(p, self)
        p.runtime_extension = \
            RunWithTime(
                RuntimeExtension(p, self, config={'jobs': 1}))

        def evaluate_calibration(e):
            from benchbuild.utils.cmd import pprof_calibrate
            papi_calibration = e.get_papi_calibration(p, pprof_calibrate)
            e.persist_calibration(p, pprof_calibrate, papi_calibration)


        actns = self.default_runtime_actions(p)
        actns.append(Calibrate(self, evaluate_calibration))
        return self.default_runtime_actions(p)

