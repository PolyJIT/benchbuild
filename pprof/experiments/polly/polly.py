#!/usr/bin/env python
# encoding: utf-8

"""
The 'polly' Experiment
====================

This experiment applies polly's transformations to all projects and measures
the runtime.

This forms the baseline numbers for the other experiments.


Measurements
------------

3 Metrics are generated during this experiment:
    time.user_s - The time spent in user space in seconds (aka virtual time)
    time.system_s - The time spent in kernel space in seconds (aka system time)
    time.real_s - The time spent overall in seconds (aka Wall clock)
"""

from pprof.experiment import step, RuntimeExperiment
from pprof.settings import config
from os import path


class Polly(RuntimeExperiment):

    """ The polly experiment. """

    def run_project(self, p):
        from uuid import uuid4
        from pprof.experiments.raw import run_with_time

        llvm_libs = path.join(config["llvmdir"], "lib")
        p.ldflags = ["-L" + llvm_libs]
        p.cflags = ["-O3",
                    "-Xclang", "-load",
                    "-Xclang", "LLVMPolyJIT.so",
                    "-mllvm", "-polly"]

        for i in range(1, int(config["jobs"]) + 1):
            p.run_uuid = uuid4()
            with step("time: {} cores & uuid {}".format(i, p.run_uuid)):
                p.clean()
                p.prepare()
                p.download()
                p.configure()
                p.build()

                run_with_time.config = config
                run_with_time.experiment = self
                run_with_time.project = p
                run_with_time.jobs = i
                p.run(run_with_time)
