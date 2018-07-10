"""
PAPI based experiments.

These types of experiments (papi & papi-std) need to instrument the
project with libbenchbuild support to work.

"""
import sqlalchemy as sa

import benchbuild.extensions as ext
import benchbuild.utils.schema as schema
from benchbuild.experiment import Experiment
from benchbuild.utils.actions import Step


class Calibrate(Step):
    NAME = "CALIBRATE"
    DESCRIPTION = "Calibrate libpapi measurement functions."


class Analyze(Step):
    NAME = "ANALYZE"
    DESCRIPTION = "Analyze the experiment after completion."


class Event(schema.BASE):
    """Store PAPI profiling based events."""

    __tablename__ = 'benchbuild_events'
    __table__args__ = {'extend_existing': True}

    name = sa.Column(sa.String, index=True)
    start = sa.Column(sa.Numeric, primary_key=True)
    duration = sa.Column(sa.Numeric)
    id = sa.Column(sa.Integer, primary_key=True)
    type = sa.Column(sa.SmallInteger)
    tid = sa.Column(sa.BigInteger)
    run_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("run.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
        primary_key=True)


class PapiScopCoverage(Experiment):
    """PAPI-based dynamic SCoP coverage measurement."""

    NAME = "papi"
    SCHEMA = [Event.__table__]

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
            "-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so", "-mllvm",
            "-polli", "-mllvm", "-polli-instrument", "-mllvm",
            "-polli-no-recompilation", "-mllvm", "-polly-detect-keep-going"
        ]
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
    SCHEMA = [Event.__table__]

    def actions_for_project(self, project):
        """
        Create & Run a papi-instrumented version of the project.

        This experiment uses the -jitable flag of libPolyJIT to generate
        dynamic SCoP coverage.
        """
        project.ldflags = project.ldflags + ["-lpjit", "-lpprof", "-lpapi"]
        project.cflags = [
            "-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so", "-mllvm",
            "-polli", "-mllvm", "-polli-instrument", "-mllvm",
            "-polli-no-recompilation", "-mllvm", "-polly-detect-keep-going"
        ]
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
