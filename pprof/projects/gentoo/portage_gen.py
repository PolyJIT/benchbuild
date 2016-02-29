"""
Generic experiment to test portage packages within gentoo chroot.
"""
from pprof.projects.gentoo.gentoo import GentooGroup
from pprof.utils.run import run, uchroot
from plumbum import local

class AutoPortage(GentooGroup):
    """
    Generic portage experiment.
    """

    def build(self):
        with local.cwd(self.builddir):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            prog = self.DOMAIN + "/" + self.NAME[len(self.DOMAIN)+1:]
            run(emerge_in_chroot[prog])

    def run_tests(self, experiment):
        pass

def PortageFactory(name, NAME, DOMAIN, BaseClass=AutoPortage):
    newclass = type(name, (BaseClass,), {
        "NAME" : NAME,
        "DOMAIN" : DOMAIN
    })
    return newclass
