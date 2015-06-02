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

    def run_step_jit(self, p):
        from plumbum.cmd import time
        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("JIT, no instrumentation"):
            p.download()
            p.ldflags = ["-L" + llvm_libs, "-lpjit", "-lpprof", "-lpapi"]

            ld_lib_path = filter(None, config["ld_library_path"].split(":"))
            p.ldflags = ["-L" + el for el in ld_lib_path] + p.ldflags
            p.cflags = ["-O3",
                        "-Xclang", "-load",
                        "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli",
                        "-mllvm", "-jitable",
                        "-mllvm", "-polly-detect-keep-going"]
            with substep("Build"):
                with local.env(PPROF_ENABLE=0):
                    p.configure()
                    p.build()
            with substep("Execute {}".format(p.name)):
                def run_with_time(run_f, *args):
                    from plumbum.cmd import time
                    from pprof.utils.db import submit
                    cmd = time["-f", "%U-%S-%e", run_f, args]
                    retcode, stdou, stderr = cmd.run()
                    run_id = create_run(
                        get_db_connection(), str(cmd), p.name, self.name, p.run_uuid)
                    timings = stderr.split('-')
                    timings = {
                        "table": "metrics",
                        "columns": ["name", "value", "run_id"],
                        "values": [
                            ("polyjit.time.user_s", timings[0], run_id),
                            ("polyjit.time.system_s", timings[1], run_id),
                            ("polyjit.time.real_s", timings[2], run_id)
                        ]
                    }
                    submit(timings)
                p.run(run_with_time)

    def run_step_likwid(self, p):
        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("JIT, likwid"):
            p.clean()
            p.prepare()
            p.download()
            p.ldflags = ["-L" + llvm_libs, "-lpjit", "-lpprof", "-lpapi"]
            ld_lib_path = filter(None, config["ld_library_path"].split(":"))
            p.ldflags = ["-L" + el for el in ld_lib_path] + p.ldflags
            p.cflags = ["-O3",
                        "-Xclang", "-load",
                        "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli",
                        "-mllvm", "-jitable",
                        "-mllvm", "-polly-detect-keep-going"]
            with substep("Build"):
                with local.env(PPROF_ENABLE=0):
                    p.configure()
                    p.build()
            with substep("Execute {}".format(p.name)):
                def run_with_likwid(run_f, args, has_stdin = False):
                    from pprof.utils.db import create_run, get_db_connection
                    from pprof.likwid import get_likwid_perfctr, to_db
                    from plumbum import local

                    likwid_f = p.name + "_%p.txt"

                    likwid_path = path.join(config["likwiddir"], "bin")
                    likwid_perfctr = local[
                        path.join(likwid_path, "likwid-perfctr")]
                    run_cmd = likwid_perfctr["-O", "-o", likwid_f, "-m", "-C",
                                             "-L:0", "-g", "CLOCK", run_f]
                    if has_stdin:
                        run_cmd = (run_cmd[args] < sys.stdin)
                    else:
                        run_cmd = run_cmd[args]

                    run_cmd()

                    run_id = create_run(
                        get_db_connection(), str(run_cmd), p.name, self.name, p.run_uuid)
                    likwid_measurement = get_likwid_perfctr(likwid_f)
                    likwid.to_db(run_id, likwid_measurement)
                p.run(run_with_likwid)

    def run_project(self, p):
        with local.env(PPROF_ENABLE=0):
            self.run_step_jit(p)
            self.run_step_likwid(p)
