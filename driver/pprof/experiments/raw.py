#!/usr/bin/env python
# encoding: utf-8

from ..experiment import RuntimeExperiment, try_catch_log
from ..settings import config
from plumbum import local, FG
from plumbum.cmd import time, awk, tee, echo, rm
from os import path
from ..experiment import Experiment as exp
import re
import csv

likwid_perfctr = None
opt = None
llc = None
asm = None
clang = None


class RawRuntime(RuntimeExperiment):

    """Just run the experiments after compiling with llc."""

    report = {
        "T_user": "User time - ([0-9.]+)",
        "T_system": "System time - ([0-9.]+)",
        "T_wall": "Wall clock - ([0-9.]+)"
    }

    def setup_commands(self):
        """setup llvm commands
        """
        super(RawRuntime, self).setup_commands()
        global opt, llc, asm, likwid_perfctr, clang
        bin_path = path.join(config["llvmdir"], "bin")

        likwid_perfctr = local[path.join(bin_path, "likwid-perfctr")]
        opt = local[path.join(bin_path, "opt")]
        llc = local[path.join(bin_path, "llc")]
        asm = local["as"]
        clang = local[path.join(bin_path, "clang")]

    @try_catch_log
    def run_project(self, p):
        """run projects after compiling the IR file with O3

        :p: the project which we want to run

        """
        base_f = p.base_f
        opt_f = p.optimized_f
        asm_f = p.asm_f
        obj_f = p.obj_f
        run_f = p.run_f
        time_f = p.time_f
        result_f = p.result_f

        opt["-O3", base_f, "-o", opt_f] & FG
        llc["-O3", "-mcpu=corei7-avx", opt_f, "-o", asm_f] & FG
        asm[asm_f, "-o", obj_f] & FG
        with local.cwd(p.sourcedir):
            clang[obj_f, p.ld_flags, "-o", run_f] & FG

        # Print header here.
        (echo["---------------------------------------------------------------"]
            >> result_f) & FG
        (echo[">>> ========= " + p.name + " Program"]
            >> result_f) & FG
        (echo["---------------------------------------------------------------"]
            >> result_f) & FG

        p.run(time["-f", "%U,%S,%e", "-a", "-o", time_f, local[run_f]])
        (awk["-F", ",", ("{ usr+=$1; sys+=$2; wall+=$3 }"
                         " END {"
                         " print \"User time - \" usr;"
                         " print \"System time - \" sys;"
                         " print \"Wall clock - \" wall;}"), time_f] |
         tee["-a", result_f]) & FG

        rm(opt_f)
        rm(obj_f)
        rm(asm_f)
        rm(run_f)

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

