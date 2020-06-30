"""Subcommand for configuration handling."""
import os

from plumbum import cli

from benchbuild import settings
from benchbuild.cli.main import BenchBuild


@BenchBuild.subcommand("config")
class BBConfig(cli.Application):
    """Manage BenchBuild's configuration."""

    def main(self):
        if not self.nested_command:
            self.help()


@BBConfig.subcommand("view")
class BBConfigView(cli.Application):
    """View the current configuration."""

    def main(self):
        print(repr(settings.CFG))


@BBConfig.subcommand("write")
class BBConfigWrite(cli.Application):
    """Write the current configuration to a file."""

    def main(self):
        config_path = ".benchbuild.yml"
        settings.CFG.store(config_path)
        print("Storing config in {0}".format(os.path.abspath(config_path)))
