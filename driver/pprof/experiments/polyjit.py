#!/usr/bin/env python
# encoding: utf-8

from ..experiment import Experiment, RuntimeExperiment, try_catch_log
from ..settings import config

from plumbum import local, FG
from plumbum.cmd import cp, awk, echo, tee, time, sed, rm
from os import path

polli = None
likwid_perfctr = None
pprof_calibrate = None
pprof_analyze = None
opt = None


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

        cp[base_f, bin_f] & FG
        polli_opts = p.ld_flags + p.polli_flags
        polli_c = polli["-fake-argv0=" + run_f, "-O3", "-lpapi", "-lpprof",
                        polli_opts,
                        "-jitable", "-polly-detect-keep-going",
                        "-polly-detect-track-failures",
                        "-polly-use-runtime-alias-checks=false",
                        "-polly-delinearize=false", bin_f]

        # 1. Run with PAPI counters
        p.run(time["-f", "%U,%S,%e", "-a", "-o", time_f,
                   polli["-fake-argv0=" + run_f, "-O3", "-lpapi", "-lpprof",
                         "-jitable", "-polly-detect-keep-going",
                         "-polly-detect-track-failures",
                         "-polly-use-runtime-alias-checks=false",
                         "-polly-delinearize=false", "-instrument",
                         "-no-recompilation", bin_f]])

        # 2. Run with likwid CLOCK group
        p.run(likwid_perfctr["-O", "-o", likwid_f, "-m", "-C", "-L:0", "-g",
                             "CLOCK", polli_c]
              )

        # 3. Run with likwid DATA GROUP
        # p.run(likwid_perfctr["-O", "-o", csv_f, "-m", "-C", "-L:0", "-g",
        #    "DATA", polli_c]
        #)

        likwid_filter = local["filters/likwid.csv"]
        likwid_filter[likwid_f, "perfctr", "-o", csv_f] & FG

        sed["-i", "s/^/" + p.domain + ",/", csv_f] & FG
        sed["-i", "s/^/" + p.name + ",/", csv_f] & FG

        # Print header here.
        (echo["---------------------------------------------------------------"]
            >> result_f) & FG
        (echo[">>> ========= " + p.name + " Program"]
            >> result_f) & FG
        (echo["---------------------------------------------------------------"]
            >> result_f) & FG

        (pprof_analyze[prof_f] | tee["-a", result_f]) & FG

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

        rm(bin_f)
        rm(prof_f)
