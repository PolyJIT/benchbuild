"""
p7zip experiment within gentoo chroot.
"""
from plumbum import local

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils import run, wrapping


class SevenZip(GentooGroup):
    """
        app-arch/p7zip
    """
    NAME = "p7zip"
    DOMAIN = "app-arch"

    def run_tests(self):
        _7z = wrapping.wrap(local.path('/usr/bin/7z'), self)
        _7z = run.watch(_7z)
        _7z("b", "-mmt1")
