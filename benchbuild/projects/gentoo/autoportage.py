import logging

from plumbum import local

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils import uchroot


class AutoPortage(GentooGroup):
    """
    Generic portage experiment.
    """

    def compile(self):
        emerge_in_chroot = uchroot.uchroot()["/usr/bin/emerge"]
        prog = self.DOMAIN + "/" + str(self.NAME)[len(self.DOMAIN) + 1:]
        with local.env(CONFIG_PROTECT="-*"):
            emerge_in_chroot(
                "--autounmask-only=y",
                "--autounmask-write=y",
                prog,
                retcode=None
            )
        uchroot.uretry(emerge_in_chroot[prog])

    def run_tests(self):
        log = logging.getLogger(__name__)
        log.warning('Not implemented')
