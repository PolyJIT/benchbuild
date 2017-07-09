"""
Generic experiment to test portage packages within gentoo chroot.
"""
import logging
from benchbuild.projects.gentoo import autoportage
from benchbuild.utils.run import run, uchroot_no_args
from benchbuild.utils.container import Gentoo
from plumbum import local, ProcessExecutionError


class FuncClass(object):

    """
    Finds out the current version number of a gentoo package.

    The package name is created by combining the domain and the name.
    Then uchroot is used to switch into a gentoo shell where the 'emerge'
    command is used to recieve the version number.
    The function then parses the version number back into the file.

    Args:
        Name: Name of the project.
        Domain: Categorie of the package.
    """

    def __init__(self, name, domain, container):
        self.name = name
        self.domain = domain
        self.container = container

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        try:
            domain, _, name = self.name.partition("_")
            package = domain + '/' + name
            container = self.container()

            uchroot = uchroot_no_args()
            uchroot = uchroot["-E", "-A", "-C", "-w", "/", "-r"]
            uchroot = uchroot[container.local]
            with local.env(CONFIG_PROTECT="-*"):
                fake_emerge = uchroot["emerge",
                                      "--autounmask-only=y",
                                      "--autounmask-write=y",
                                      "--nodeps"]
                run(fake_emerge[package])

            emerge_in_chroot = uchroot["emerge",
                                       "-p",
                                       "--nodeps",
                                       package]
            _, stdout, _ = emerge_in_chroot.run()

            for line in stdout.split('\n'):
                if package in line:
                    _, _, package_name = line.partition("/")
                    _, name, version = package_name.partition(name)
                    version, _, _ = version.partition(" ")
                    return version[1:]
        except ProcessExecutionError:
            logger = logging.getLogger(__name__)
            logger.info("This older package might not exist any more.")
        return "Default"


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

    def run_not_supported(self, *args, **kwargs):  # pylint: disable=W0613
        """Dynamic projects don't support a run() test."""
        from benchbuild.settings import CFG
        logger = logging.getLogger(__name__)
        logger.info("run() not supported.")
        if CFG["clean"].value():
            self.clean()
        return

    newclass = type(name, (BaseClass,), {
        "NAME": NAME,
        "DOMAIN": DOMAIN,
        "SRC_FILE": "none",
        "VERSION": FuncClass(NAME, DOMAIN, Gentoo),
        "GROUP": "auto-gentoo",
        "run": run_not_supported,
        "__module__": "__main__"
    })
    return newclass
