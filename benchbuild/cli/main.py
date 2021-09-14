"""Main CLI unit of BenchBuild."""
import os

from plumbum import cli

from benchbuild import plugins, settings
from benchbuild.utils import log


class BenchBuild(cli.Application):
    """Frontend for running/building the benchbuild study framework."""

    VERSION = str(settings.CFG["version"])
    _list_env = False

    verbosity = cli.CountOf('-v', help="Enable verbose output")
    debug = cli.Flag('-d', help="Enable debugging output")
    force_tty = cli.Flag('--force-tty', help="Assume an available tty")
    force_watch_unbuffered = cli.Flag(
        '--force-watch-unbuffered',
        help="Force watched commands to output unbuffered"
    )

    def main(self, *args: str) -> int:
        cfg = settings.CFG

        self.verbosity = self.verbosity if self.verbosity < 6 else 5
        if self.debug:
            self.verbosity = 3
        verbosity = int(os.getenv('BB_VERBOSITY', self.verbosity))

        cfg["verbosity"] = verbosity
        cfg["debug"] = self.debug
        cfg["force_tty"] = self.force_tty
        cfg["force_watch_unbuffered"] = self.force_watch_unbuffered

        log.configure()
        log.set_defaults()

        plugins.discover()

        if cfg["db"]["create_functions"]:
            from benchbuild.utils.schema import init_functions, Session
            init_functions(Session())

        if args:
            print("Unknown command {0!r}".format(args[0]))
            return 1
        if not self.nested_command:
            self.help()

        return 0
