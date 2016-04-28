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

import os
import re
import uuid
import warnings

from pprof.utils.run import partial
from pprof.experiment import step, RuntimeExperiment
from pprof.settings import CFG

class ShouldNotBeNone(RuntimeWarning):
    """User warning, if config var is null."""
    pass

class PollyPerformance(RuntimeExperiment):
    """ The polly performance experiment. """

    NAME = "pollyperformance"

    def run_project(self, p):
        from pprof.experiments.raw import run_with_time

        configs = CFG["perf"]["config"].value()
        if configs is None:
            warnings.warn("({0}) should not be null.".format(repr(CFG["perf"]["config"])),
                          category=ShouldNotBeNone, stacklevel=2)
            return

        config_list = re.split(r'\s*', configs)

        config_with_llvm = []
        for config in config_list:
            config_with_llvm.append("-mllvm")
            config_with_llvm.append(config)

        llvm_libs = os.path.join(CFG["llvm"]["dir"].value(), "lib")
        llvm_libs = CFG["llvm"]["dir"].value()
        p.ldflags = ["-L" + llvm_libs]
        p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                    "-mllvm", "-polly"] + config_with_llvm

        jobs = CFG["jobs"].value()
        for i in range(1, int(jobs) + 1):
            p.run_uuid = uuid.uuid4()
            with step("time: {0} cores & uuid {1}".format(i, p.run_uuid)):
                p.clean()
                p.prepare()
                p.download()
                p.configure()
                p.build()
                p.run(partial(run_with_time, p, self, CFG, i))
