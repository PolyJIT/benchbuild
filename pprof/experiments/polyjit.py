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

        with step("JIT, no instrumentation"):
            p.download()
            p.ldflags = ["-L" + llvm_libs, "-lpjit", "-lpprof", "-lpapi"]

            ld_lib_path = filter(None, config["ld_library_path"].split(":"))
            p.ldflags = [ "-L"+el for el in ld_lib_path] + p.ldflags
            p.cflags = ["-O3",
                        "-Xclang", "-load",
                        "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli",
                        "-mllvm", "-jitable",
                        "-mllvm", "-polly-detect-keep-going"]
            with substep("reconf & rebuild"):
                p.configure()
                p.build()
            with substep("run {}".format(p.name)):
                def runner(run_f):
                    return time[run_f]
                p.run(runner)

        with step("JIT, likwid"):
            p.clean()
            p.prepare()
            p.download()
            p.ldflags = ["-L" + llvm_libs, "-lpjit"]
            p.cflags = ["-O3",
                        "-Xclang", "-load",
                        "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli",
                        "-mllvm", "-jitable",
                        "-mllvm", "-polly-detect-keep-going"]
            with substep("reconf & rebuild"):
                p.configure()
                p.build()
            with substep("run {}".format(p.name)):
                def runner(run_f):
                    return likwid_perfctr["-O", "-o", p.likwid_f, "-m", "-C",
                                          "-L:0", "-g", "CLOCK", run_f]
                p.run(runner)

            with substep("Create DB entry & evaluate likwid run"):
                run_id = create_run(
                    get_db_connection(), "likwid", p.name, self.name, p.run_uuid)
                likwid_measurement = likwid.get_likwid_perfctr(p.likwid_f)
                likwid.to_db(run_id, likwid_measurement)
