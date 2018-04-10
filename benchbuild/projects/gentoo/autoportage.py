import logging

from plumbum import local

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.run import uchroot, uretry


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

    def run_tests(self, experiment, runner):
        del experiment, runner # Unused
        log = logging.getLogger(__name__)
        log.warning('Not implemented')
