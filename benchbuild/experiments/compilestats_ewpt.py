"""
The 'compilestats_ewpt' Experiment.

Gathers compilation statistics for compiling the project with the
EWPT alias analysis enabled.

"""

from benchbuild.experiments.compilestats import CompilestatsExperiment


class EWPTCompilestatsExperiment(CompilestatsExperiment):
    """Experiment that collects compilestats with EWPT enabled."""
    NAME = "ewpt"

    def extra_cflags(self):
        return ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                "-mllvm", "-polly"]
