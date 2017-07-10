"""
The 'pprof' Experiment.

TODO Description
"""
import benchbuild.experiment as exp
import benchbuild.extensions as ext


class PProfExperiment(exp.Experiment):
    """The pprof experiment with fancy description."""

    NAME = "profileScopDetection"

    def actions_for_project(self, project):
        project.cflags = ["-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                "-O3",
                "-mllvm", "-profileScopDetection"]
        project.ldflags = ["-lpjit"]
        project.runtime_extension = ext.RunWithTime(
                ext.RuntimeExtension(project, self, config={})
            )

        return self.default_runtime_actions(project)
