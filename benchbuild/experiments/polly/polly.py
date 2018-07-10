"""
This experiment applies polly's transformations to all projects and measures
the runtime.
"""
from benchbuild.experiment import Experiment
from benchbuild.extensions import RunWithTime, RuntimeExtension
from benchbuild.settings import CFG


class Polly(Experiment):
    """The polly experiment."""

    NAME = "polly"

    def actions_for_project(self, project):
        """Compile & Run the experiment with -O3 enabled."""
        project.cflags = ["-O3", "-fno-omit-frame-pointer",
                          "-Xclang", "-load",
                          "-mllvm", "-stats",
                          "-Xclang", "LLVMPolly.so",
                          "-mllvm", "-polly"]
        project.runtime_extension = \
            RunWithTime(
                RuntimeExtension(project, self,
                                 {'jobs': int(CFG["jobs"].value())}))

        return self.default_runtime_actions(project)
