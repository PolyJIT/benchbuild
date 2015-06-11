#!/usr/bin/env python
# encoding: utf-8

"""
The 'raw' Experiment
====================

This experiment is the basic experiment in the pprof study. It simply runs
all projects after compiling it with -O3. The binaries are wrapped
with the time command and results are written to the database.

This forms the baseline numbers for the other experiments.

Measurements
------------

3 Metrics are generated during this experiment:
    raw.time.user_s - The time spent in user space in seconds (aka virtual time)
    raw.time.system_s - The time spent in kernel space in seconds (aka system time)
    raw.time.real_s - The time spent overall in seconds (aka Wall clock)
"""

from pprof.experiment import step, substep, RuntimeExperiment
from pprof.settings import config
from pprof.utils.db import create_run, RunResult
from os import path


class RawRuntime(RuntimeExperiment):

    """ The polyjit experiment """

    def run_project(self, p):
        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("RAW -O3"):
            p.ldflags = ["-L" + llvm_libs]
            p.cflags = ["-O3"]
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
                        raw.time.user_s - The time spent in user space in
                                          seconds (aka virtual time)
                        raw.time.system_s - The time spent in kernel space in
                                            seconds (aka system time)
                        raw.time.real_s - The time spent overall in seconds
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
                    from pprof.utils.run import fetch_time_output, handle_stdin

                    project_name = kwargs.get("project_name", p.name)
                    timing_tag = "PPROF-RAW: "
                    timing_format = timing_tag + "%U-%S-%e"
                    timing_unformat = timing_tag + "{:g}-{:g}-{:g}"

                    run_cmd = handle_stdin(
                        time["-f", timing_format, run_f, args], kwargs)

                    _, _, stderr = run_cmd.run()
                    timings = fetch_time_output(timing_tag, timing_unformat,
                                                stderr.split("\n"))
                    if len(timings) == 0:
                        return

                    run_id = create_run(str(run_cmd), project_name, self.name,
                                        p.run_uuid)

                    for t in timings:
                        d = {
                            "table": "metrics",
                            "columns": ["name", "value", "run_id"],
                            "values": [
                                ("raw.time.user_s", t[0], run_id),
                                ("raw.time.system_s", t[1], run_id),
                                ("raw.time.real_s", t[2], run_id)
                            ]
                        }
                        submit(d)

                p.run(run_with_time)
