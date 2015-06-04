#!/usr/bin/env python
# encoding: utf-8

from pprof import likwid
from pprof.experiment import step, substep, Experiment, RuntimeExperiment
from pprof.settings import config
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
                def run_with_time(run_f, args, **kwargs):
                    from plumbum.cmd import time
                    from pprof.utils.db import submit
                    from pprof.project import fetch_time_output
                    import sys

                    has_stdin = kwargs.get("has_stdin", False)
                    project_name = kwargs.get("project_name", p.name)

                    run_cmd = time["-f", "PPROF-JIT: %U-%S-%e", run_f]
                    if has_stdin:
                        run_cmd = (run_cmd[args] < sys.stdin)
                    else:
                        run_cmd = run_cmd[args]
                    _, _, stderr = run_cmd.run()
                    timings = fetch_time_output("PPROF-JIT: ",
                                                "PPROF-JIT: {:g}-{:g}-{:g}",
                                                stderr.split("\n"))
                    if len(timings) == 0:
                        return

                    run_id = create_run(
                        get_db_connection(), str(run_cmd), project_name,
                        self.name, p.run_uuid)

                    for t in timings:
                        d = {
                            "table": "metrics",
                            "columns": ["name", "value", "run_id"],
                            "values": [
                                ("time.user_s", t[0], run_id),
                                ("time.system_s", t[1], run_id),
                                ("time.real_s", t[2], run_id)
                            ]
                        }
                        submit(d)

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
                def run_with_likwid(run_f, args, **kwargs):
                    from pprof.utils.db import create_run, get_db_connection
                    from pprof.likwid import get_likwid_perfctr, to_db
                    from plumbum.cmd import rm
                    from plumbum import local
                    import sys

                    has_stdin = kwargs.get("has_stdin", False)
                    project_name = kwargs.get("project_name", p.name)

                    likwid_f = p.name + ".txt"

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
                        get_db_connection(), str(run_cmd), project_name,
                        self.name, p.run_uuid)
                    likwid_measurement = get_likwid_perfctr(likwid_f)
                    likwid.to_db(run_id, likwid_measurement)
                    rm("-f", likwid_f)
                p.run(run_with_likwid)

    def run_project(self, p):
        with local.env(PPROF_ENABLE=0):
            self.run_step_jit(p)
            self.run_step_likwid(p)
