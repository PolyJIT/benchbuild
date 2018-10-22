"""
eix experiment within gentoo chroot
"""
from plumbum import local

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.wrapping import wrap


class Eix(GentooGroup):
    """Represents the package eix from the portage tree."""

    NAME = 'eix'
    DOMAIN = 'app-portage'

    def run_tests(self, runner):
        """Runs runtime tests for eix"""

        eix = wrap(local.path('/') / 'usr' / 'bin' / 'eix', self)
        runner(eix["clang"])
