#!/usr/bin/env python3
from benchbuild import settings
from benchbuild.utils import log
from plumbum import cli


class PollyProfiling(cli.Application):
    """Frontend for running/building the benchbuild study framework."""

    VERSION = settings.CFG["version"].value()
    _list_env = False

    verbosity = cli.CountOf('-v', help="Enable verbose output")

    def main(self, *args):
        self.verbosity = self.verbosity if self.verbosity < 4 else 3
        settings.CFG["verbosity"] = self.verbosity

        log.configure()
        log.set_defaults()
        settings.update_env()

        if args:
            print("Unknown command {0!r}".format(args[0]))
            return 1
        if not self.nested_command:
            self.help()


def main(*args):
    """Main function."""
    PollyProfiling.subcommand("bootstrap",
                              "benchbuild.bootstrap.BenchBuildBootstrap")
    PollyProfiling.subcommand("run", "benchbuild.run.BenchBuildRun")
    PollyProfiling.subcommand("log", "benchbuild.log.BenchBuildLog")
    PollyProfiling.subcommand("test", "benchbuild.test.BenchBuildTest")
    PollyProfiling.subcommand("slurm", "benchbuild.slurm.Slurm")
    PollyProfiling.subcommand("report", "benchbuild.report.BenchBuildReport")
    return PollyProfiling.run(*args)
