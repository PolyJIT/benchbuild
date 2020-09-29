import os

from plumbum import cli

from benchbuild import settings
from benchbuild.utils import bootstrap

CFG = settings.CFG


class BenchBuildBootstrap(cli.Application):
    """Bootstrap benchbuild external dependencies, if possible."""

    store_config = cli.Flag(["-s", "--save-config"],
                            help="Save benchbuild's configuration.",
                            default=False)

    def main(self, *args: str) -> int:
        del args  # Unused

        print("Checking benchbuild binary dependencies...")
        bootstrap.provide_package("cmake")
        bootstrap.provide_package("fusermount")
        bootstrap.provide_package("unionfs")
        bootstrap.provide_package(
            'uchroot', installer=bootstrap.install_uchroot
        )
        bootstrap.provide_packages(CFG['bootstrap']['packages'].value)

        if self.store_config:
            config_path = ".benchbuild.yml"
            CFG.store(config_path)
            print("Storing config in {0}".format(os.path.abspath(config_path)))
        return 0
