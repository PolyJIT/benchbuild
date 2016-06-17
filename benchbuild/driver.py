#!/usr/bin/env python3
import logging
import os
import sys
from benchbuild import settings
from benchbuild.utils import log
from plumbum.machines.local import LocalEnv
from plumbum import cli, local


class PollyProfiling(cli.Application):
    """ Frontend for running/building the benchbuild study framework """

    VERSION = settings.CFG["version"].value()
    _list_env = False

    verbosity = cli.CountOf('-v', help="Enable verbose output")

    @cli.switch(
        ["--list-env"],
        help=
        "List all environment variables that affect this program's behavior and exit."
    )
    def list_env(self):
        self._list_env = True

    def do_list_env(self):
        """List config metadata."""
        for setting in settings.config_metadata:
            if "env" in setting:
                print(("{env}\t-\t{desc}".format(env=setting["env"],
                                                 desc=setting["desc"] if "desc"
                                                 in setting else '')))

    def main(self, *args):
        if self._list_env:
            # List environment variables and exit.
            self.do_list_env()
            return

        log_levels = {
            3: logging.DEBUG,
            2: logging.INFO,
            1: logging.WARNING,
            0: logging.ERROR
        }

        self.verbosity = self.verbosity if self.verbosity < 4 else 3
        logging.captureWarnings(True)

        log.configure()
        LOG = logging.getLogger()
        LOG.setLevel(log_levels[self.verbosity])

        settings.update_env()

        if args:
            print("Unknown command {0!r}".format(args[0]))
            return 1
        if not self.nested_command:
            print("No command given")
            return 1


def main(*args):
    """Main function."""
    PollyProfiling.subcommand("run", "benchbuild.run.BenchBuildRun")
    PollyProfiling.subcommand("build", "benchbuild.build.Build")
    PollyProfiling.subcommand("log", "benchbuild.log.BenchBuildLog")
    PollyProfiling.subcommand("test", "benchbuild.test.BenchBuildTest")
    PollyProfiling.subcommand("slurm", "benchbuild.slurm.Slurm")
    return PollyProfiling.run(*args)
