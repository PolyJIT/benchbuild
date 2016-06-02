"""
Generic experiment to test portage packages within gentoo chroot.
"""
import logging
from benchbuild.projects.gentoo import autoportage

def PortageFactory(name, NAME, DOMAIN, BaseClass=autoportage.AutoPortage):
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
        >>> from benchbuild.projects.gentoo.portage_gen import PortageFactory
        >>> from benchbuild.experiments.empty import Empty
        >>> c = PortageFactory("test", "NAME", "DOMAIN")
        >>> c
        <class '__main__.test'>
        >>> i = c(Empty())
        >>> i.NAME
        'NAME'
        >>> i.DOMAIN
        'DOMAIN'
    """

    def run_not_supported(self, *args, **kwargs): # pylint: disable=W0613
        """Dynamic projects don't support a run() test."""
        from benchbuild.settings import CFG
        logger = logging.getLogger(__name__)
        logger.info("run() not supported.")
        if CFG["clean"].value():
            self.clean()
        return

    newclass = type(name, (BaseClass,), {
        "NAME" : NAME,
        "DOMAIN" : DOMAIN,
        "GROUP" : "auto-gentoo",
        "run" : run_not_supported,
        "__module__" : "__main__"
    })
    return newclass
