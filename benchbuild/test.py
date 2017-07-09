#!/usr/bin/env python3
from plumbum import cli
from benchbuild.driver import PollyProfiling
from benchbuild.settings import CFG
import os


@PollyProfiling.subcommand("test")
class BenchBuildTest(cli.Application):
    """
        Create regression tests for polyjit from the measurements database.
    """

    @cli.switch(["-P", "--prefix"],
                str,
                help="Prefix for our regression-test image.")
    def prefix(self, prefix):
        CFG["regression_prefix"] = os.path.abspath(prefix)

    def opt_flags(self):
        return ["-load", "LLVMPolyJIT.so", "-O3", "-jitable", "-polli",
                "-polly-only-scop-detection", "-polly-delinearize=false",
                "-polly-detect-keep-going", "-no-recompilation",
                "-polli-analyze", "-disable-output", "-stats"]

    def get_check_line(self, name, module):
        from plumbum import local
        from benchbuild.utils.compiler import llvm_libs
        from benchbuild.utils.cmd import sed, opt

        with local.env(LD_LIBRARY_PATH=llvm_libs()):
            # Magic. ;-)
            ret, _, err = \
                (opt[self.opt_flags()] <<
                    (sed[r"0,/\#0/s///"] << module)()).run(retcode=None)
            if not ret == 0:
                print(("{0} is broken:".format(name)))
                print(err)

        return """
; CHECK: 1 polyjit          - Number of jitable SCoPs

"""

    def main(self):
        from benchbuild.utils.schema import Session, RegressionTest
        from benchbuild.utils.cmd import mkdir, sed

        prefix = CFG["regression-prefix"]
        if not os.path.exists(prefix):
            mkdir("-p", prefix)

        session = Session()
        for elem in session.query(RegressionTest).order_by(
                RegressionTest.project_name):
            sub_dir = os.path.join(prefix, elem.project_name)
            if not os.path.exists(sub_dir):
                mkdir("-p", sub_dir)

            test_path = os.path.join(sub_dir, elem.name + ".ll")
            with open(test_path, 'w') as test_f:
                test_f.write("""
; RUN: opt {opt_flags} < %s 2>&1 | FileCheck %s
""".format(opt_flags=" ".join(self.opt_flags())))
                test_f.write(self.get_check_line(test_path, elem.module))
                test_f.write(elem.module)
            (sed["-i", r"0,/\#0/s///", test_path])()
