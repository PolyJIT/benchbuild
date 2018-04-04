"""
The 'compilestats' experiment.

This experiment is a basic experiment in the benchbuild study. It simply runs
all projects after compiling it with -O3 and catches all statistics emitted
by llvm.

"""
from benchbuild.experiment import Experiment
import benchbuild.extensions as ext


class CompilestatsExperiment(Experiment):
    """The compilestats experiment."""

    NAME = "cs"

    def actions_for_project(self, project):
        project.compiler_extension = \
            ext.RunWithTimeout(ext.ExtractCompileStats(project, self))
        return CompilestatsExperiment.default_compiletime_actions(project)


class PollyCompilestatsExperiment(Experiment):
    """The compilestats experiment with polly enabled."""

    NAME = "p-cs"

    def actions_for_project(self, project):
        project.cflags = ["-O3",
                          "-Xclang", "-load",
                          "-Xclang", "LLVMPolly.so",
                          "-mllvm", "-polly"]
        project.compiler_extension = \
            ext.RunWithTimeout(ext.ExtractCompileStats(project, self))
        return CompilestatsExperiment.default_compiletime_actions(project)
