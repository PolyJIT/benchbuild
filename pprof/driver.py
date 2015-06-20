#!/usr/bin/env python
# encoding: utf-8

from plumbum import cli
from pprof import *
from sys import stderr
import logging


class PollyProfiling(cli.Application):

    """ Frontend for running/building the pprof study framework """

    VERSION = "0.9.6"

    @cli.switch(["-v", "--verbose"], help="Enable verbose output")
    def verbose(self):
        LOG = logging.getLogger()
        LOG.addHandler(logging.StreamHandler(stderr))
        LOG.setLevel(logging.DEBUG)

    def main(self, *args):
        if args:
            print "Unknown command %r" % (args[0],)
            return 1
        if not self.nested_command:
            print "No command given"
            return 1


def main(*args):
    return PollyProfiling.run(*args)
