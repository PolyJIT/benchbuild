#!/usr/bin/env python
# encoding: utf-8

from pprof.experiment import RuntimeExperiment
from pprof.experiment import step, substep
from pprof.settings import config
from pprof.utils.db import create_run

from plumbum import local
from os import path

pprof_calibrate = None
pprof_analyze = None


class PapiScopCoverage(RuntimeExperiment):

    """ The polyjit experiment """

    def setup_commands(self):
        super(PapiScopCoverage, self).setup_commands()
        global pprof_calibrate, pprof_analyze
        bin_path = path.join(config["llvmdir"], "bin")

        pprof_calibrate = local[path.join(bin_path, "pprof-calibrate")]
        pprof_analyze = local[path.join(bin_path, "pprof-analyze")]

    def run(self):
        """
        Do the postprocessing, after all projects are done.
        """
        super(PapiScopCoverage, self).run()
        with local.env(PPROF_EXPERIMENT_ID=str(config["experiment"]),
                       PPROF_EXPERIMENT=self.name,
                       PPROF_USE_DATABASE=1,
                       PPROF_USE_FILE=0,
                       PPROF_USE_CSV=0):
            pprof_analyze()

    def run_project(self, p):
        from plumbum.cmd import time

        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("Class: Dynamic, PAPI"):
            p.download()
            p.ldflags = ["-L" + llvm_libs, "-lpjit", "-lpprof", "-lpapi"]

            ld_lib_path = filter(None, config["ld_library_path"].split(":"))
            p.ldflags = ["-L" + el for el in ld_lib_path] + p.ldflags
            p.cflags = ["-O3",
                        "-Xclang", "-load",
                        "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli",
                        "-mllvm", "-jitable",
                        "-mllvm", "-instrument",
                        "-mllvm", "-no-recompilation",
                        "-mllvm", "-polly-detect-keep-going"]
            with substep("reconf & rebuild"):
                with local.env(PPROF_ENABLE=0):
                    p.configure()
                    p.build()
            with substep("run"):
                def run_with_time(run_f, args, **kwargs):
                    from plumbum.cmd import time
                    from pprof.utils.db import TimeResult
                    from pprof.utils.run import fetch_time_output, handle_stdin

                    project_name = kwargs.get("project_name", p.name)

                    run_cmd = handle_stdin(
                        time["-f", "PPROF-PAPI: %U-%S-%e", run_f, args], kwargs)

                    _, _, stderr = run_cmd.run()
                    timings = fetch_time_output("PPROF-PAPI: ",
                                                "PPROF-PAPI: {:g}-{:g}-{:g}",
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

        with step("Evaluation"):
            papi_calibration = self.get_papi_calibration(
                p, pprof_calibrate)
            if papi_calibration:
                from pprof.utils.db import TimeResult

                run_id = create_run(
                    str(pprof_calibrate), p.name, self.name, p.run_uuid)

                result = TimeResult()
                result.append(
                    ("papi.calibration.time_ns", papi_calibration, run_id))
                result.commit()


class PapiStandardScopCoverage(PapiScopCoverage):

    """ PAPI Scop Coverage, without JIT """

    def run_project(self, p):
        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("Class: Standard - PAPI"):
            p.download()
            p.ldflags = ["-L" + llvm_libs, "-lpjit", "-lpprof", "-lpapi"]

            ld_lib_path = filter(None, config["ld_library_path"].split(":"))
            p.ldflags = ["-L" + el for el in ld_lib_path] + p.ldflags
            p.cflags = ["-O3",
                        "-Xclang", "-load",
                        "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli",
                        "-mllvm", "-instrument",
                        "-mllvm", "-no-recompilation",
                        "-mllvm", "-polly-detect-keep-going"]
            with substep("reconf & rebuild"):
                with local.env(PPROF_ENABLE=0):
                    p.configure()
                    p.build()
            with substep("run"):
                def run_with_time(run_f, args, **kwargs):
                    from plumbum.cmd import time
                    from pprof.utils.db import TimeResult
                    from pprof.utils.run import fetch_time_output, handle_stdin

                    project_name = kwargs.get("project_name", p.name)

                    run_cmd = handle_stdin(
                        time["-f", "%U-%S-%e", run_f, args], kwargs)

                    _, _, stderr = run_cmd.run()
                    timings = fetch_time_output("PPROF-PAPI: ",
                                                "PPROF-PAPI: {:g}-{:g}-{:g}",
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

        with step("Evaluation"):
            papi_calibration = self.get_papi_calibration(
                p, pprof_calibrate)
            if papi_calibration:
                from pprof.utils.db import TimeResult

                run_id = create_run(
                    str(pprof_calibrate), p.name, self.name, p.run_uuid)
                result = TimeResult()
                result.append(
                    ("papi.calibration.time_ns", papi_calibration, run_id))
                result.commit()
