"""
The 'compilestats_ewpt' Experiment.

Gathers compilation statistics for compiling the project with the
EWPT alias analysis enabled.

"""

from pprof.experiments.compilestats import CompilestatsExperiment


class EWPTCompilestatsExperiment(CompilestatsExperiment):
    def extra_cflags(self):
        return ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                "-mllvm", "-polly"]
