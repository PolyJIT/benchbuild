#!/usr/bin/env python3
import logging
from pprof import settings
from pprof.utils import logging as plog
from plumbum import cli

class PollyProfiling(cli.Application):
    """ Frontend for running/building the pprof study framework """

    VERSION = "1.0"
    _config_path = "./.pprof_config.py"
    _list_env = False

    verbosity = cli.CountOf('-v', help="Enable verbose output")

    @cli.switch(
        ["-c", "--config"],
        str,
        help=
        "File path of the config file. Generate a configuration file with `pprof config -o filename.py`"
    )
    def config_path(self, filepath):
        self._config_path = filepath

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

        plog.configure()
        LOG = logging.getLogger()
        LOG.setLevel(log_levels[self.verbosity])

        if args:
            print("Unknown command {0!r}".format(args[0] ))
            return 1
        if not self.nested_command:
            print("No command given")
            return 1


def main(*args):
    """Main function."""
    PollyProfiling.subcommand("run", "pprof.run.PprofRun")
    PollyProfiling.subcommand("build", "pprof.build.Build")
    PollyProfiling.subcommand("log", "pprof.log.PprofLog")
    PollyProfiling.subcommand("test", "pprof.test.PprofTest")
    PollyProfiling.subcommand("config", "pprof.generate_config.PprofGenConfig")
    PollyProfiling.subcommand("slurm", "pprof.slurm.Slurm")
    return PollyProfiling.run(*args)
