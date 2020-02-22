"""
eix experiment within gentoo chroot
"""
from plumbum import local



from benchbuild.projects.gentoo.gentoo import GentooGroup


class Eix(GentooGroup):
    """Represents the package eix from the portage tree."""

    NAME = 'eix'
    DOMAIN = 'app-portage'

    def run_tests(self):
        """Runs runtime tests for eix"""

        eix = wrapping.wrap(local.path('/usr/bin/eix'), self)
        eix = run.watch(eix)
        eix("clang")
