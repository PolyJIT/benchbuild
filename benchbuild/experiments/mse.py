"""
Test Maximal Static Expansion.

This tests the maximal static expansion implementation by
Nicholas Bonfante (implemented in LLVM/Polly).
"""
from benchbuild.extensions import ExtractCompileStats
from benchbuild.experiment import RuntimeExperiment
from benchbuild.extensions import RunWithTime, RuntimeExtension
from benchbuild.settings import CFG


class PollyMSE(RuntimeExperiment):
    """The polly experiment."""

    NAME = "polly-mse"

    def actions_for_project(self, project):
        """Compile & Run the experiment with -O3 enabled."""
        project.cflags = [
            "-O3",
            "-fno-omit-frame-pointer",
            "-mllvm", "-polly",
            "-mllvm", "-polly-enable-mse",
            "-mllvm", "-polly-process-unprofitable",
            "-mllvm", "-polly-enable-optree=0",
            "-mllvm", "-polly-enable-delicm=0",
        ]
        project.compiler_extension = ExtractCompileStats(project, self)
        project.runtime_extension = \
            RunWithTime(
                RuntimeExtension(project, self,
                                 config={'jobs': int(CFG["jobs"].value())}))

        return self.default_runtime_actions(project)
