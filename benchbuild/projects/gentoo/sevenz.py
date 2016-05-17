"""
p7zip experiment within gentoo chroot.
"""
from os import path
from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.run import run, uchroot
from plumbum import local


class SevenZip(GentooGroup):
    """
        app-arch/p7zip
    """
    NAME = "gentoo-7z"
    DOMAIN = "app-arch"

    def build(self):
        with local.cwd(self.builddir):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            run(emerge_in_chroot["app-arch/p7zip"])

    def run_tests(self, experiment):
        from benchbuild.project import wrap

        wrap(path.join(self.builddir, "usr", "bin", "7z"), experiment,
             self.builddir)
        sevenz = uchroot()["/usr/bin/7z"]
        run(sevenz["b", "-mmt1"])
