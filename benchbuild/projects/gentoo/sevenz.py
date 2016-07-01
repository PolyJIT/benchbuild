"""
p7zip experiment within gentoo chroot.
"""
from os import path
from benchbuild.project import wrap
from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.run import run, uchroot


class SevenZip(GentooGroup):
    """
        app-arch/p7zip
    """
    NAME = "gentoo-7z"
    DOMAIN = "app-arch"

    def build(self):
        emerge_in_chroot = uchroot()["/usr/bin/emerge"]
        run(emerge_in_chroot["app-arch/p7zip"])

    def run_tests(self, experiment):
        wrap(
            path.join(self.builddir, "usr", "bin", "7z"), experiment,
            self.builddir)
        sevenz = uchroot()["/usr/bin/7z"]
        run(sevenz["b", "-mmt1"])
