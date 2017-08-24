import logging

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.run import uretry, uchroot
from plumbum import local


class AutoPortage(GentooGroup):
    """
    Generic portage experiment.
    """

    def build(self):
        emerge_in_chroot = uchroot()["/usr/bin/emerge"]
        prog = self.DOMAIN + "/" + str(self.NAME)[len(self.DOMAIN) + 1:]
        with local.env(CONFIG_PROTECT="-*"):
            emerge_in_chroot("--autounmask-only=y",
                             "--autounmask-write=y",
                             prog,
                             retcode=None)
        uretry(emerge_in_chroot[prog])

    def run_tests(self, *args, **kwargs):
        log = logging.getLogger(__name__)
        log.warn('Not implemented')
