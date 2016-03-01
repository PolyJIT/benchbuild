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
            prog = self.DOMAIN + "/" + str(self.NAME)[len(self.DOMAIN)+1:]
            run(emerge_in_chroot[prog])

    def run_tests(self, experiment):
        pass

def PortageFactory(name, NAME, DOMAIN, BaseClass=AutoPortage):
    """
    Create a new dynamic portage project.

    Auto-Generated projects can only be used for compilie-time experiments,
    because there simply is no run-time test defined for it. Therefore,
    we implement the run symbol as a noop (with minor logging).

    This way we avoid the default implementation for run() that all projects
    inherit.

    Args:
        name: Name of the dynamic class.
        NAME: NAME property of the dynamic class.
        DOMAIN: DOMAIN property of the dynamic class.
        BaseClass: Base class to use for the dynamic class.

    Returns:
        A new class with NAME,DOMAIN properties set, unable to perform
        run-time tests.

    Examples:
        >>> from pprof.projects.gentoo.portage_gen import PortageFactory
        >>> from pprof.experiments.empty import Empty
        >>> c = PortageFactory("test", "NAME", "DOMAIN")
        >>> c
        <class 'pprof.projects.gentoo.portage_gen.test'>
        >>> i = c(Empty())
        >>> i.NAME
        'NAME'
        >>> i.DOMAIN
        'DOMAIN'
    """
    newclass = type(name, (BaseClass,), {
        "NAME" : NAME,
        "DOMAIN" : DOMAIN
    })
    return newclass
