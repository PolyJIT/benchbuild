import os
from plumbum import cli
import benchbuild.utils.bootstrap as bs
from benchbuild.settings import CFG

provide_package = bs.provide_package
provide_packages = bs.provide_packages
find_package = bs.find_package
install_package = bs.find_package
install_uchroot = bs.install_uchroot
check_uchroot_config = bs.check_uchroot_config


class BenchBuildBootstrap(cli.Application):
    """Bootstrap benchbuild external dependencies, if possible."""

    store_config = cli.Flag(["-s", "--save-config"],
                            help="Save benchbuild's configuration.",
                            default=False)

    def main(self, *args):
        print("Checking benchbuild binary dependencies...")
        provide_package("cmake")
        provide_package("fusermount")
        provide_package("unionfs")
        provide_package("postgres")

        has_uchroot = find_package("uchroot")
        if not has_uchroot:
            install_uchroot()
            has_uchroot = find_package("uchroot")
            if not has_uchroot:
                print("NOT INSTALLED")
        if has_uchroot:
            check_uchroot_config()

        provide_packages([
            "mkdir", "git", "tar", "mv", "rm", "bash", "rmdir", "time",
            "chmod", "cp", "ln", "make", "unzip", "cat", "patch", "find",
            "echo", "grep", "sed", "sh", "autoreconf", "ruby", "curl", "tail",
            "kill", "virtualenv", "timeout"
        ])

        if self.store_config:
            config_path = ".benchbuild.yml"
            CFG.store(config_path)
            print("Storing config in {0}".format(os.path.abspath(config_path)))
            exit(0)
