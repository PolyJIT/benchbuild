#!/usr/bin/env python
# encoding: utf-8

from plumbum import cli
from settings import config

import sys
import logging


class PollyProfiling(cli.Application):

    """ Frontend for running/building the pprof study framework """

    VERSION = "0.8.1"

    @cli.switch(["-v", "--verbose"], help="Enable verbose output")
    def verbose(self):
        log.setLevel(logging.DEBUG)

    def main(self, *args):
        if args:
            print "Unknown command %r" % (args[0],)
            return 1
        if not self.nested_command:
            print "No command given"
            return 1


log = logging.getLogger()
handler = logging.StreamHandler(sys.stderr)
log.addHandler(handler)
log.setLevel(logging.WARNING)


def main(*args):
    from pprof import run
    from pprof import build

    return PollyProfiling.run(*args)
