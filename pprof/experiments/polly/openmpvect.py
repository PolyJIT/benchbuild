#!/usr/bin/env python
# encoding: utf-8

"""
The 'polly-openmp-vectorize' Experiment.

This experiment applies polly's transformations with openmp code generation
enabled to all projects and measures the runtime.

This forms the baseline numbers for the other experiments.

Measurements
------------

3 Metrics are generated during this experiment:
    time.user_s - The time spent in user space in seconds (aka virtual time)
    time.system_s - The time spent in kernel space in seconds (aka system time)
    time.real_s - The time spent overall in seconds (aka Wall clock)
"""

from pprof.experiment import step, substep, RuntimeExperiment
from pprof.settings import config
from os import path


class PollyOpenMPVectorizer(RuntimeExperiment):

    """Timing experiment with Polly & OpenMP+Vectorizer support."""

    def run_project(self, p):
        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("Polly, OpenMP & Vectorizer=stripmine"):
            p.ldflags = ["-L" + llvm_libs, "-lgomp"]
            p.cflags = ["-O3",
                        "-Xclang", "-load",
                        "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polly",
                        "-mllvm", "-polly-parallel",
                        "-mllvm", "-polly-vectorizer=stripmine"]
            with substep("reconf & rebuild"):
                p.download()
                p.configure()
                p.build()
            with substep("run {}".format(p.name)):
                from pprof.experiments.raw import run_with_time

                run_with_time.config = config
                run_with_time.experiment = self
                run_with_time.project = p
                run_with_time.jobs = config["jobs"]

                p.run(run_with_time)
