"""
PAPI based experiments.

These types of experiments (papi & papi-std) need to instrument the
project with libbenchbuild support to work.

"""
from benchbuild.experiment import Experiment
import benchbuild.extensions as ext
from benchbuild.utils.actions import Step


class Calibrate(Step):
    NAME = "CALIBRATE"
    DESCRIPTION = "Calibrate libpapi measurement functions."


class Analyze(Step):
    NAME = "ANALYZE"
    DESCRIPTION = "Analyze the experiment after completion."


class PapiScopCoverage(Experiment):
    """PAPI-based dynamic SCoP coverage measurement."""

    NAME = "papi"

    def actions(self):
        """Do the postprocessing, after all projects are done."""
        actions = super(PapiScopCoverage, self).actions()

        return actions

    def actions_for_project(self, project):
        """
        Create & Run a papi-instrumented version of the project.

        This experiment uses the -jitable flag of libPolyJIT to generate
        dynamic SCoP coverage.
        """
        project.ldflags = project.ldflags + ["-lpjit", "-lpprof", "-lpapi"]
        project.cflags = [
            "-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
            "-mllvm", "-polli",
            "-mllvm", "-polli-instrument",
            "-mllvm", "-polli-no-recompilation",
            "-mllvm", "-polly-detect-keep-going"]
        project.compiler_extension = \
            ext.RunWithTimeout(ext.ExtractCompileStats(project, self))
        project.runtime_extension = \
            ext.RunWithTime(
                ext.RuntimeExtension(project, self, config={'jobs': 1}))

        def evaluate_calibration(e):
            from benchbuild.utils.cmd import pprof_calibrate
            papi_calibration = e.get_papi_calibration(pprof_calibrate)
            e.persist_calibration(project, pprof_calibrate, papi_calibration)

        actns = self.default_runtime_actions(project)
        actns.append(Calibrate(self, evaluate_calibration))
        return self.default_runtime_actions(project)


class PapiStandardScopCoverage(PapiScopCoverage):
    """PAPI Scop Coverage, without JIT."""

    NAME = "papi-std"

    def actions_for_project(self, project):
        """
        Create & Run a papi-instrumented version of the project.

        This experiment uses the -jitable flag of libPolyJIT to generate
        dynamic SCoP coverage.
        """
        project.ldflags = project.ldflags + ["-lpjit", "-lpprof", "-lpapi"]
        project.cflags = [
            "-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
            "-mllvm", "-polli",
            "-mllvm", "-polli-instrument",
            "-mllvm", "-polli-no-recompilation",
            "-mllvm", "-polly-detect-keep-going"]
        project.compiler_extension = \
            ext.RunWithTimeout(ext.ExtractCompileStats(project, self))
        project.runtime_extension = \
            ext.RunWithTime(
                ext.RuntimeExtension(project, self, config={'jobs': 1}))

        def evaluate_calibration(e):
            from benchbuild.utils.cmd import pprof_calibrate
            papi_calibration = e.get_papi_calibration(pprof_calibrate)
            e.persist_calibration(project, pprof_calibrate, papi_calibration)

        actns = self.default_runtime_actions(project)
        actns.append(Calibrate(self, evaluate_calibration))
        return self.default_runtime_actions(project)
