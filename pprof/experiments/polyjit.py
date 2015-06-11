#!/usr/bin/env python
# encoding: utf-8

"""
The 'polyjit' experiment. This experiment uses likwid to measure the
performance of all binaries when running with polyjit support enabled.
"""

from pprof import likwid
from pprof.experiment import step, substep, RuntimeExperiment
from pprof.settings import config

from plumbum import local
from os import path


class PolyJIT(RuntimeExperiment):

    """ The polyjit experiment """

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
                    from pprof.utils.db import TimeResult, create_run
                    from pprof.utils.run import fetch_time_output, handle_stdin

                    project_name = kwargs.get("project_name", p.name)
                    timing_tag = "PPROF-JIT: "

                    run_cmd = time["-f", timing_tag + "%U-%S-%e", run_f]
                    run_cmd = handle_stdin(run_cmd[args], kwargs)
                    _, _, stderr = run_cmd.run()

                    timings = fetch_time_output(timing_tag,
                                                timing_tag + "{:g}-{:g}-{:g}",
                                                stderr.split("\n"))
                    if len(timings) == 0:
                        return

                    run_id = create_run(str(run_cmd), project_name, self.name,
                                        p.run_uuid)

                    result = TimeResult()
                    for timing in timings:
                        result.append(("time.user_s", timing[0], run_id))
                        result.append(("time.system_s", timing[1], run_id))
                        result.append(("time.real_s", timing[2], run_id))
                    result.commit()
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
                    from pprof.utils.db import create_run
                    from pprof.utils.run import handle_stdin
                    from pprof.likwid import get_likwid_perfctr
                    from plumbum.cmd import rm

                    project_name = kwargs.get("project_name", p.name)
                    likwid_f = p.name + ".txt"

                    for group in ["CLOCK", "DATA", "ENERGY"]:
                        likwid_path = path.join(config["likwiddir"], "bin")
                        likwid_perfctr = local[
                            path.join(likwid_path, "likwid-perfctr")]
                        run_cmd = likwid_perfctr["-O", "-o", likwid_f, "-m", "-C",
                                                 "-L:0", "-g", group, run_f]

                        run_cmd = handle_stdin(run_cmd[args], kwargs)
                        run_cmd()

                        run_id = create_run(
                            str(run_cmd), project_name, self.name, p.run_uuid)
                        likwid_measurement = get_likwid_perfctr(likwid_f)
                        likwid.to_db(run_id, likwid_measurement)
                        rm("-f", likwid_f)
                p.run(run_with_likwid)

    def run_project(self, p):
        with local.env(PPROF_ENABLE=0):
            self.run_step_jit(p)
            self.run_step_likwid(p)
