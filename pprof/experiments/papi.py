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


class PapiScopCoverage(RuntimeExperiment):

    """ The polyjit experiment """

    def setup_commands(self):
        super(PapiScopCoverage, self).setup_commands()
        global polli, likwid_perfctr, pprof_calibrate, pprof_analyze, opt
        bin_path = path.join(config["llvmdir"], "bin")
        likwid_path = path.join(config["likwiddir"], "bin")

        likwid_perfctr = local[path.join(likwid_path, "likwid-perfctr")]
        polli = local[path.join(bin_path, "polli")]
        pprof_calibrate = local[path.join(bin_path, "pprof-calibrate")]
        pprof_analyze = local[path.join(bin_path, "pprof-analyze")]
        opt = local[path.join(bin_path, "opt")]

    def run(self):
        super(PapiScopCoverage, self).run()
        """ Do the postprocessing, after all projects are done."""
        with local.env(PPROF_EXPERIMENT_ID=str(config["experiment"]),
                       PPROF_EXPERIMENT=self.name,
                       PPROF_USE_DATABASE=1,
                       PPROF_USE_FILE=0,
                       PPROF_USE_CSV=0):
            pprof_analyze()

    def run_project(self, p):
        from plumbum.cmd import time

        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("No recompilation, PAPI"):
            p.download()
            p.ldflags = ["-L" + llvm_libs, "-lpjit", "-lpprof", "-lpapi"]

            ld_lib_path = filter(None, config["ld_library_path"].split(":"))
            p.ldflags = [ "-L"+el for el in ld_lib_path] + p.ldflags
            p.cflags = ["-O3",
                        "-Xclang", "-load",
                        "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli",
                        "-mllvm", "-jitable",
                        "-mllvm", "-instrument",
                        "-mllvm", "-no-recompilation",
                        "-mllvm", "-polly-detect-keep-going"]
            with substep("reconf & rebuild"):
                p.configure()
                p.build()
            with substep("run"):
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
                            ("papi.time.user_s", timings[0], run_id),
                            ("papi.time.system_s", timings[1], run_id),
                            ("papi.time.real_s", timings[2], run_id)
                        ]
                    }
                    submit(timings)
                p.run(run_with_time)

        with step("Evaluation"):
            papi_calibration = self.get_papi_calibration(
                p, pprof_calibrate)
            if papi_calibration:
                from pprof.utils.db import submit

                run_id = create_run(
                    get_db_connection(), str(pprof_calibrate), p.name,
                    self.name, p.run_uuid)
                metrics = {
                    "table": "metrics",
                    "columns": ["name", "value", "run_id"],
                    "values": []
                }

                metrics["values"].append(
                    ("papi.calibration.time_ns", papi_calibration, run_id))
                submit(metrics)
