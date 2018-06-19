"""
gzip experiment within gentoo chroot.
"""
from os import path

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.cmd import tar
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import uchroot, uretry
from benchbuild.utils.wrapping import wrap_in_uchroot as wrap


class GZip(GentooGroup):
    """
        app-arch/gzip
    """
    NAME = "gentoo-gzip"
    DOMAIN = "app-arch"

    test_url = "http://lairosiel.de/dist/"
    test_archive = "compression.tar.gz"
    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    def prepare(self):
        super(GZip, self).prepare()

        test_archive = self.test_archive
        test_url = self.test_url + test_archive
        Wget(test_url, test_archive)
        tar("fxz", test_archive)

    def build(self):
        emerge_in_chroot = uchroot()["/usr/bin/emerge"]
        uretry(emerge_in_chroot["app-arch/gzip"])

    def run_tests(self, runner):
        wrap(
            path.join(self.builddir, "bin", "gzip"), self, self.builddir)
        gzip = uchroot()["/bin/gzip"]

        # Compress
        runner(gzip["-f", "-k", "--best", "compression/text.html"])
        runner(gzip["-f", "-k", "--best", "compression/chicken.jpg"])
        runner(gzip["-f", "-k", "--best", "compression/control"])
        runner(gzip["-f", "-k", "--best", "compression/input.source"])
        runner(gzip["-f", "-k", "--best", "compression/liberty.jpg"])

        # Decompress
        runner(gzip["-f", "-k", "--decompress", "compression/text.html.gz"])
        runner(gzip["-f", "-k", "--decompress", "compression/chicken.jpg.gz"])
        runner(gzip["-f", "-k", "--decompress", "compression/control.gz"])
        runner(gzip["-f", "-k", "--decompress", "compression/input.source.gz"])
        runner(gzip["-f", "-k", "--decompress", "compression/liberty.jpg.gz"])
