#!/usr/bin/env python3
from plumbum import cli
from pprof.driver import PollyProfiling
from pprof.settings import CFG
from pprof.utils.user_interface import query_yes_no
from plumbum.cmd import mkdir
import os, os.path


@PollyProfiling.subcommand("gentoo")
class Gentoo(cli.Application):
    """ Frontend for running experiments in the pprof study framework. """

    @cli.switch(["-S", "--sourcedir"], str, help="Where are the source files")
    def sourcedir(self, dirname):
        CFG["sourcedir"] = dirname

    @cli.switch(["--llvm-srcdir"], str, help="Where are the llvm source files")
    def llvm_sourcedir(self, dirname):
        CFG["llvm-srcdir"] = dirname

    @cli.switch(["-B", "--builddir"], str, help="Where should we build")
    def builddir(self, dirname):
        CFG["builddir"] = dirname

    @cli.switch(["--likwid-prefix"], str, help="Where is likwid installed?")
    def likwiddir(self, dirname):
        CFG["likwiddir"] = dirname

    @cli.switch(["-L", "--llvm-prefix"], str, help="Where is llvm?")
    def llvmdir(self, dirname):
        CFG["llvmdir"] = dirname

    def main(self):
        # Only try to create the build dir if we're actually running some projects.
        builddir = os.path.abspath(CFG["builddir"])
        if not os.path.exists(builddir):
            response = query_yes_no(
                "The build directory {dirname} does not exist yet. Create it?".format(
                    dirname=builddir),
                "no")
            if response:
                mkdir("-p", builddir)

        from pprof.project import ProjectRegistry
        from pprof.projects.gentoo import gentoo
        from pprof.experiments import empty

        exp = empty.Empty(["stage3"])
        exp.clean()
        exp.prepare()
        exp.run()
