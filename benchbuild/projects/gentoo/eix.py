"""
eix experiment within gentoo chroot
"""
from os import path
from benchbuild.utils.wrapping import wrap_in_uchroot as wrap
from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.run import run, uchroot


class Eix(GentooGroup):
    """Represents the package eix from the portage tree."""

    NAME = 'eix'
    DOMAIN = 'app-portage'

    def build(self):
        """Compiles and installes eix within gentoo chroot"""

        emerge_in_chroot = uchroot()["/usr/bin/emerge"]
        run(emerge_in_chroot["eix"])

    def run_tests(self, experiment, run):
        """Runs runtime tests for eix"""

        wrap(path.join("usr", "bin", "eix"), experiment, self.builddir)
        eix = uchroot()["/usr/bin/eix"]

        run(eix["clang"])
