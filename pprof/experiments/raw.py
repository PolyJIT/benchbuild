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
        p.download()
        p.cflags = ["-O3"]
        p.configure()
        p.build()

        # Print header here.
        (echo["---------------------------------------------------------------"]
            >> p.result_f) & FG
        (echo[">>> ========= " + p.name + " Program"]
            >> p.result_f) & FG
        (echo["---------------------------------------------------------------"]
            >> p.result_f) & FG

        p.run(time["-f", "%U,%S,%e", "-a", "-o", p.time_f, local[p.run_f]])
        (awk["-F", ",", ("{ usr+=$1; sys+=$2; wall+=$3 }"
                         " END {"
                         " print \"User time - \" usr;"
                         " print \"System time - \" sys;"
                         " print \"Wall clock - \" wall;}"), time_f] |
         tee["-a", p.result_f]) & FG

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

