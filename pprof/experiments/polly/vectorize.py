#!/usr/bin/env python
# encoding: utf-8

"""
The 'polly-vectorize' Experiment
====================

This experiment applies polly's transformations with stripmine vectorizer
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
from pprof.utils.db import create_run
from os import path


class PollyVectorizer(RuntimeExperiment):

    """ The polyjit experiment """

    def run_project(self, p):
        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("Polly, vectorizer stripmine"):
            p.ldflags = ["-L" + llvm_libs]
            p.cflags = ["-O3",
                        "-Xclang", "-load",
                        "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polly",
                        "-mllvm", "-polly-vectorizer=stripmine"]
            with substep("reconf & rebuild"):
                p.download()
                p.configure()
                p.build()
            with substep("run {}".format(p.name)):
                def run_with_time(run_f, args, **kwargs):
                    """
                    Function runner for the raw experiment.
                    This executes the given project command wrapped in the
                    time command. Afterwards the result is sent to the
                    database.

                    3 Metrics are generated during this experiment:
                        time.user_s - The time spent in user space in
                                      seconds (aka virtual time)
                        time.system_s - The time spent in kernel space in
                                        seconds (aka system time)
                        time.real_s - The time spent overall in seconds
                                      (aka Wall clock)

                    :run_f:
                        The file we actually execute.
                    :args:
                        Arguments to forwards to :run_f:
                    :has_stdin:
                        If the program requires access to a file redirected
                        via stdin, say so.
                    :project_name:
                        Name of the project to enter into the db.
                    :kwargs:
                        Rest.
                    """
                    from plumbum.cmd import time
                    from pprof.utils.db import TimeResult
                    from pprof.utils.run import fetch_time_output, handle_stdin
                    import sys

                    project_name = kwargs.get("project_name", p.name)

                    run_cmd = handle_stdin(
                        time["-f", "PPROF-POLLY: %U-%S-%e", run_f, args], kwargs)
                    _, _, stderr = run_cmd.run()
                    timings = fetch_time_output("PPROF-POLLY: ",
                                                "PPROF-POLLY: {:g}-{:g}-{:g}",
                                                stderr.split("\n"))
                    if len(timings) == 0:
                        return

                    run_id = create_run(
                        str(run_cmd), project_name, self.name, p.run_uuid)

                    result = TimeResult()
                    for timing in timings:
                        result.append(("time.user_s", timing[0], run_id))
                        result.append(("time.system_s", timing[1], run_id))
                        result.append(("time.real_s", timing[2], run_id))
                    result.commit()

                p.run(run_with_time)
