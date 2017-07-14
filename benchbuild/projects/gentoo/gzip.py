"""
gzip experiment within gentoo chroot.
"""
from os import path
from benchbuild.utils.wrapping import wrap_in_uchroot as wrap
from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import uretry, uchroot
from benchbuild.utils.cmd import tar  # pylint: disable=E0401


run = uretry


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
        run(emerge_in_chroot["app-arch/gzip"])

    def run_tests(self, experiment, run):
        wrap(
            path.join(self.builddir, "bin", "gzip"), experiment, self.builddir)
        gzip = uchroot()["/bin/gzip"]

        # Compress
        run(gzip["-f", "-k", "--best", "compression/text.html"])
        run(gzip["-f", "-k", "--best", "compression/chicken.jpg"])
        run(gzip["-f", "-k", "--best", "compression/control"])
        run(gzip["-f", "-k", "--best", "compression/input.source"])
        run(gzip["-f", "-k", "--best", "compression/liberty.jpg"])

        # Decompress
        run(gzip["-f", "-k", "--decompress", "compression/text.html.gz"])
        run(gzip["-f", "-k", "--decompress", "compression/chicken.jpg.gz"])
        run(gzip["-f", "-k", "--decompress", "compression/control.gz"])
        run(gzip["-f", "-k", "--decompress", "compression/input.source.gz"])
        run(gzip["-f", "-k", "--decompress", "compression/liberty.jpg.gz"])
