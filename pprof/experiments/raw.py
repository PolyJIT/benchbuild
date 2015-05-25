#!/usr/bin/env python
# encoding: utf-8

from ..experiment import Experiment, RuntimeExperiment, try_catch_log
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
                def runner(run_f):
                    return time["-f", "%U,%S,%e", "-a", "-o", p.time_f, run_f]
                p.run(runner)

        with step("Evaluation"):
            # Print header here.
            (echo["---------------------------------------------------------------"]
                >> p.result_f)()
            (echo[">>> ========= " + p.name + " Program"]
                >> p.result_f)()
            (echo["---------------------------------------------------------------"]
                >> p.result_f)()

            (awk["-F", ",", ("{ usr+=$1; sys+=$2; wall+=$3 }"
                             " END {"
                             " print \"\";"
                             " print \"User time - \" usr;"
                             " print \"System time - \" sys;"
                             " print \"Wall clock - \" wall;}"), p.time_f] |
             tee["-a", p.result_f]) & FG
