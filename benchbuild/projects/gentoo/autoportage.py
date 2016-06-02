from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.run import run, uchroot
from plumbum import local

class AutoPortage(GentooGroup):
    """
    Generic portage experiment.
    """

    def build(self):
        with local.cwd(self.builddir):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            prog = self.DOMAIN + "/" + str(self.NAME)[len(self.DOMAIN)+1:]
            with local.env(CONFIG_PROTECT="-*"):
                emerge_in_chroot("--autounmask-only=y", "--autounmask-write=y",
                                 prog, retcode=None)
            run(emerge_in_chroot[prog])

    def run_tests(self, _):
        log = logging.getLogger('benchbuild')
        log.warn('Not implemented')
