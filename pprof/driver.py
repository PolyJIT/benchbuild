#!/usr/bin/env python
# encoding: utf-8

from plumbum import cli
from pprof import *
from sys import stderr
import os.path
import logging
from pprof import settings

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(filename)s.%(funcName)s:%(lineno)s - %(message)s', datefmt='%H:%M:%S',
                    level=logging.WARN)

class PollyProfiling(cli.Application):

    """ Frontend for running/building the pprof study framework """

    VERSION = "0.9.8"
    _config_path = "./.pprof_config.py"
    _list_env = False

    @cli.switch(["-v", "--verbose"], help="Enable verbose output")
    def verbose(self):
        """Enable verbose output."""
        LOG = logging.getLogger()
        LOG.addHandler(logging.StreamHandler(stderr))
        LOG.setLevel(logging.DEBUG)

    @cli.switch(["-c", "--config"], str, help="File path of the config file. Generate a configuration file with `pprof config -o filename.py`")
    def config_path(self, filepath):
        self._config_path = filepath

    @cli.switch(["--list-env"], help="List all environment variables that affect this program's behavior and exit.")
    def list_env(self):
        self._list_env = True

    def do_list_env(self):
        """List config metadata."""
        for setting in settings.config_metadata:
            if "env" in setting:
                print("{env}\t-\t{desc}".format(
                    env=setting["env"],
                    desc=setting["desc"] if "desc" in setting else ''))


    def main(self, *args):
        if self._list_env:
            # List environment variables and exit.
            self.do_list_env()
            return

        self._config_path = os.path.abspath(self._config_path)
        if os.path.exists(self._config_path):
            if settings.load_config(self._config_path, settings.config):
                print("Configuration loaded from file " + self._config_path)

        if args:
            print "Unknown command %r" % (args[0],)
            return 1
        if not self.nested_command:
            print "No command given"
            return 1


def main(*args):
    """Main function."""
    return PollyProfiling.run(*args)
