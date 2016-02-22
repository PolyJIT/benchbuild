"""
Generic experiment to test portage packages within gentoo chroot.
"""
from os import path
from pprof.projects.gentoo.gentoo import GentooGroup
from pprof.utils.run import run, uchroot
from plumbum import local


class Portage_Gen(GentooGroup):
    """
    Generic portage experiment. {domain}/{ebuild}
        Set with environment variable PPROF_EBUILD
    """

    PREFIX = "gentoo-"
    NAME = PREFIX + "{domain}.{ebuild}"
    DOMAIN = "{domain}"

    def build(self):
        with local.cwd(self.builddir):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            prog = Portage_Gen.DOMAIN + "/" + Portage_Gen.NAME.split('.')[1]
            run(emerge_in_chroot[prog])

    def run_tests(self, experiment):
        pass
