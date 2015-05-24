#!/usr/bin/env python
# encoding: utf-8

from ..experiment import RuntimeExperiment, try_catch_log
from ..experiment import Experiment as exp
from ..settings import config

from plumbum import local, FG
from plumbum.cmd import awk, echo, tee, time, rm, mv
from os import path

import csv

polli = None
likwid_perfctr = None
pprof_calibrate = None
pprof_analyze = None
opt = None


class Polli(RuntimeExperiment):

    """ Polli experiment """

    report = {
        "Runs": "Total number of program runs - ([0-9]+)",
        "T_SCoP_ns": "Time Spent in SCoPs \[ns\] - ([0-9]+)",
        "T_SCoP_s": "Time Spent in SCoPs \[s\] - ([0-9.]+)",
        "T_all_ns": "Total run-time \[ns\] - ([0-9.]+)",
        "T_all_s": "Total run-time \[s\] - ([0-9.]+)",
        "DynCov": "Dynamic SCoP coverage - ([0-9.]+)",
        "T_papi": "Time spent in libPAPI \(s\) - ([0-9.]+)",
        "T_perpapi": "Real time per PAPI call \(ns\) - ([0-9.]+)",
        "T_user": "User time - ([0-9.]+)",
        "T_system": "System time - ([0-9.]+)",
        "T_wall": "Wall clock - ([0-9.]+)"
    }

    def setup_commands(self):
        super(Polli, self).setup_commands()
        global polli, likwid_perfctr, pprof_calibrate, pprof_analyze, opt
        bin_path = path.join(config["llvmdir"], "bin")

        polli = local[path.join(bin_path, "polli")]
        likwid_perfctr = local[path.join(bin_path, "likwid-perfctr")]
        pprof_calibrate = local[path.join(bin_path, "pprof-calibrate")]
        pprof_analyze = local[path.join(bin_path, "pprof-analyze")]
        opt = local[path.join(bin_path, "opt")]

    @try_catch_log
    def run_project(self, p):
        base_f = p.base_f
        opt_f = p.optimized_f
        run_f = p.run_f
        bin_f = p.bin_f
        time_f = p.time_f
        profbin_f = p.profbin_f
        prof_f = p.prof_f
        likwid_f = p.likwid_f
        csv_f = p.csv_f
        calls_f = p.calls_f
        result_f = p.result_f

        # Preoptimize with static preoptimization sequence
        popt = opt["-load", "LLVMPolly.so"]
        popt = popt[
            "-mem2reg",
            "-early-cse",
            "-functionattrs",
            "-instcombine",
            "-globalopt",
            "-sroa",
            "-gvn",
            "-ipsccp",
            "-basicaa",
            "-simplifycfg",
            "-jump-threading",
            "-loop-unroll",
            "-globaldce",
            "-polly-prepare"]
        popt = popt["-o", opt_f]
        popt[base_f] & FG

        self.verify_product(opt_f)

        mv(opt_f, bin_f)

        # Run with PAPI counters enabled, but without own preoptimization
        # and without recompilation.
        polli_opts = p.ld_flags + p.polli_flags
        polli_c = polli["-fake-argv0=" + run_f, "-O3", "-lpapi", "-lpprof",
                        polli_opts]
        polli_c = polli_c["-instrument", "-no-recompilation", "-disable-preopt"]
        polli_c = polli_c[bin_f]
        p.run(time["-f", "%U,%S,%e", "-a", "-o", time_f, polli_c])

        self.verify_product(time_f)
        self.verify_product(prof_f)
        rm(bin_f)

        # Print header here.
        (echo["---------------------------------------------------------------"]
            >> result_f) & FG
        (echo[">>> ========= " + p.name + " Program"]
            >> result_f) & FG
        (echo["---------------------------------------------------------------"]
            >> result_f) & FG

        (pprof_analyze[prof_f] | tee["-a", result_f]) & FG
        rm(prof_f)

        papi_calibration = self.get_papi_calibration(p, pprof_calibrate)
        if papi_calibration:
            (awk[("{s+=$1} END {"
                  " time = (s*" + papi_calibration + "/1000000000);"
                  " print \"Time spent in libPAPI (s) - \" time }"
                  ),
                 calls_f] |
             tee["-a", result_f]) & FG
            (echo["Real time per PAPI call (ns) - ", papi_calibration] |
                tee["-a", result_f]) & FG

        (awk["-F", ",", ("{ usr+=$1; sys+=$2; wall+=$3 }"
                         " END {"
                         " print \"User time - \" usr;"
                         " print \"System time - \" sys;"
                         " print \"Wall clock - \" wall;}"), time_f] |
         tee["-a", result_f]) & FG

    def generate_report(self, per_project_results):
        csv_f = self.result_f + ".csv"
        results = []
        for project_result in per_project_results:
            prj = self.projects[project_result[0]]
            payload = project_result[1]
            prefix = {"Name": prj.name, "Domain": prj.domain}
            results.append(exp.parse_result(self.report, prefix, payload))

        if len(results) > 0:
            fieldnames = ["Name", "Domain"] + self.report.keys()
            with open(csv_f, "wb") as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                for tup in results:
                    writer.writerow(tup)
