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


class PolyJIT(RuntimeExperiment):

    """ The polyjit experiment """

    def setup_commands(self):
        super(PolyJIT, self).setup_commands()
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

        with step("Downloading {}".format(p.name)):
            p.download()

        with step("RAW -O3"):
            p.ldflags = ["-L" + llvm_libs, "-lpjit"]
            p.cflags = ["-O3"]
            with substep("reconfigure"):
                p.configure()
            with substep("rebuild"):
                p.build()
            with substep("run"):
                p.run(time[p.run_f])

        with step("JIT, no instrumentation"):
            p.ldflags = ["-L" + llvm_libs, "-lpjit"]
            p.cflags = ["-O3",
                        "-Xclang", "-load",
                        "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli",
                        "-mllvm", "-jitable",
                        "-mllvm", "-polly-detect-keep-going"]
            with substep("reconfigure"):
                p.configure()
            with substep("rebuild"):
                p.build()
            with substep("run"):
                p.run(time[p.run_f])

        with step("JIT, likwid"):
            p.ldflags = ["-L" + llvm_libs, "-lpjit"]
            p.cflags = ["-O3",
                        "-Xclang", "-load",
                        "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli",
                        "-mllvm", "-jitable",
                        "-mllvm", "-polly-detect-keep-going"]
            with substep("reconfigure"):
                p.configure()
            with substep("rebuild"):
                p.build()
            exp_cmd = likwid_perfctr["-O", "-o", p.likwid_f, "-m", "-C", "-L:0",
                                     "-g", "CLOCK", p.run_f]
            with substep("run"):
                p.run(exp_cmd)
            with substep("Create DB entry & evaluate likwid run"):
                run_id=create_run(
                    get_db_connection(), str(exp_cmd), p.name, self.name, p.run_uuid)
                likwid_measurement=likwid.get_likwid_perfctr(p.likwid_f)
                likwid.to_db(run_id, likwid_measurement)
                for (region, name, core_info, li) in likwid_measurement:
                    print "{} - {} - {} - {}".format(region, name, core_info, li)

        with step("No recompilation, PAPI"):
            p.ldflags=["-L" + llvm_libs, "-lpjit", "-lpprof", "-lpapi"]
            p.cflags=["-O3",
                        "-Xclang", "-load",
                        "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli",
                        "-mllvm", "-jitable",
                        "-mllvm", "-instrument",
                        "-mllvm", "-no-recompilation",
                        "-mllvm", "-polly-detect-keep-going"]
            p.configure()
            p.build()
            p.run(time["-f", "%U,%S,%e", "-a", "-o", p.time_f, p.run_f])

        with step("Evaluation"):
            # Print header here.
            (echo["---------------------------------------------------------------"]
                >> p.result_f) & FG
            (echo[">>> ========= " + p.name + " Program"]
                >> p.result_f) & FG
            (echo["---------------------------------------------------------------"]
                >> p.result_f) & FG

            with substep("pprof analyze"):
                with local.env(PPROF_USE_DATABASE=1,
                               PPROF_DB_RUN_GROUP=p.run_uuid,
                               PPROF_USE_FILE=0,
                               PPROF_USE_CSV=0):
                    (pprof_analyze | tee["-a", p.result_f]) & FG

            with substep("pprof calibrate"):
                papi_calibration=self.get_papi_calibration(p, pprof_calibrate)
                if papi_calibration:
                    (awk[("{s+=$1} END {"
                          " time = (s*" + papi_calibration + "/1000000000);"
                          " print \"Time spent in libPAPI (s) - \" time }"
                          ),
                         p.calls_f] |
                     tee["-a", p.result_f]) & FG
                    (echo["Real time per PAPI call (ns) - ", papi_calibration] |
                        tee["-a", p.result_f]) & FG

            (awk["-F", ",", ("{ usr+=$1; sys+=$2; wall+=$3 }"
                             " END {"
                             " print \"User time - \" usr;"
                             " print \"System time - \" sys;"
                             " print \"Wall clock - \" wall;}"), p.time_f] |
             tee["-a", p.result_f]) & FG
