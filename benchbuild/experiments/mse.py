"""
Test Maximal Static Expansion.

This tests the maximal static expansion implementation by
Nicholas Bonfante (implemented in LLVM/Polly).
"""
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
            "-mllvm", "-stats",
            "-mllvm", "-polly",
            "-mllvm", "-polly-enable-mse",
            "-mllvm", "-polly-process-unprofitable",
            "-mllvm", "-polly-optree-analyze-known=0",
            "-mllvm", "-polly-enable-delicm=0",
        ]
        project.runtime_extension = \
            RunWithTime(
                RuntimeExtension(project, self,
                                 {'jobs': int(CFG["jobs"].value())}))

        return self.default_runtime_actions(project)
