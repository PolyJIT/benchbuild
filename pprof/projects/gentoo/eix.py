"""
eix experiment within gentoo chroot
"""
from os import path
from pprof.projects.gentoo.gentoo import GentooGroup
from pprof.utils.downloader import Wget
from pprof.utils.run import run, uchroot
from plumbum import local
from plumbum.cmd import tar  # pylint: disable=E0401

class Eix(GentooGroup):
    """Represents the package eix from the portage tree."""

    NAME = 'eix'
    DOMAIN = 'app-portage'

    def build(self):
        """Compiles and installes eix within gentoo chroot"""

        with local.cwd(self.builddir):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            run(emerge_in_chroot["eix"])

    def run_tests(self, experiment):
        """Runs runtime tests for eix"""
        from pprof.project import wrap

        wrap(path.join(self.builddir, "usr", "bin", "bzip2"), experiment,
             self.builddir)
        eix = uchroot()["/usr/bin/eix"]
        run(eix)
        run(eix["clang"])
