"""
get packages infos from gentoo chroot
"""
from pprof.projects.gentoo.portage_gen import Portage_Gen
from pprof.utils.run import run, uchroot
from plumbum import local
from pprof.settings import config

class Info(Portage_Gen):
    """
    Info experiment to retrieve package information from portage.
    """

    NAME = "gentoo-info"
    DOMAIN = "info"

    def build(self):
        with local.cwd(self.builddir):
            with local.env(CC="gcc", CXX="g++"):
                emerge_in_chroot = uchroot()["/usr/bin/emerge"]
                run(emerge_in_chroot["app-portage/portage-utils"])

            qgrep_in_chroot = uchroot()["/usr/bin/qgrep"]
            file_location = config["pprof-gentoo-autotest"]
            (qgrep_in_chroot["-l", "tc-getCC"] > file_location)()

