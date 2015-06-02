#!/usr/bin/env python
# encoding: utf-8

from ..experiment import Experiment, RuntimeExperiment
from pprof.experiment import step, substep
from ..settings import config
from pprof import likwid
from pprof.utils.db import create_run, get_db_connection

from plumbum import local, FG
from plumbum.cmd import cp, awk, echo, tee, time, sed, rm
from os import path

polli = None
likwid_perfctr = None
pprof_calibrate = None
pprof_analyze = None
opt = None

import pdb


class RawRuntime(RuntimeExperiment):

    """ The polyjit experiment """

    def setup_commands(self):
        super(RawRuntime, self).setup_commands()
        global polli, likwid_perfctr, pprof_calibrate, pprof_analyze, opt
        bin_path = path.join(config["llvmdir"], "bin")
        likwid_path = path.join(config["likwiddir"], "bin")

        likwid_perfctr = local[path.join(likwid_path, "likwid-perfctr")]
        polli = local[path.join(bin_path, "polli")]
        pprof_calibrate = local[path.join(bin_path, "pprof-calibrate")]
        pprof_analyze = local[path.join(bin_path, "pprof-analyze")]
        opt = local[path.join(bin_path, "opt")]

    def run_project(self, p):
        from plumbum.cmd import time

        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("RAW -O3"):
            p.ldflags = ["-L" + llvm_libs]
            p.cflags = ["-O3"]
            with substep("reconf & rebuild"):
                p.download()
                p.configure()
                p.build()
            with substep("run {}".format(p.name)):
                def run_with_time(run_f, args, has_stdin = False):
                    from plumbum.cmd import time
                    from pprof.utils.db import submit
                    run_cmd = time["-f", "%U-%S-%e", run_f]
                    if has_stdin:
                        run_cmd = ( run_cmd[args] < sys.stdin )
                    else:
                        run_cmd = run_cmd[args]
                    retcode, stdou, stderr = run_cmd.run()
                    run_id = create_run(
                        get_db_connection(), str(run_cmd), p.name, self.name, p.run_uuid)
                    timings = stderr.split('-')
                    timings = {
                        "table": "metrics",
                        "columns": ["name", "value", "run_id"],
                        "values": [
                            ("raw.time.user_s", timings[0], run_id),
                            ("raw.time.system_s", timings[1], run_id),
                            ("raw.time.real_s", timings[2], run_id)
                        ]
                    }
                    submit(timings)
                p.run(run_with_time)
