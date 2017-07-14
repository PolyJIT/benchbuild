"""
bzip2 experiment within gentoo chroot.
"""
from os import path

from benchbuild.utils.wrapping import wrap_in_uchroot as wrap
from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import uretry, uchroot
from benchbuild.utils.cmd import tar  # pylint: disable=E0401


run = uretry


class BZip2(GentooGroup):
    """
        app-arch/bzip2
    """
    NAME = "gentoo-bzip2"
    DOMAIN = "app-arch"
    VERSION = "1.0.6"

    test_url = "http://lairosiel.de/dist/"
    test_archive = "compression.tar.gz"
    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    def prepare(self):
        super(BZip2, self).prepare()

        test_archive = self.test_archive
        test_url = self.test_url + test_archive
        Wget(test_url, test_archive)
        tar("fxz", test_archive)

    def build(self):
        emerge_in_chroot = uchroot()["/usr/bin/emerge"]
        run(emerge_in_chroot["app-arch/bzip2"])

    def run_tests(self, experiment, run):
        wrap(
            path.join(self.builddir, "bin", "bzip2"), experiment,
            self.builddir)
        bzip2 = uchroot()["/bin/bzip2"]

        # Compress
        run(bzip2["-f", "-z", "-k", "--best", "compression/text.html"])
        run(bzip2["-f", "-z", "-k", "--best", "compression/chicken.jpg"])
        run(bzip2["-f", "-z", "-k", "--best", "compression/control"])
        run(bzip2["-f", "-z", "-k", "--best", "compression/input.source"])
        run(bzip2["-f", "-z", "-k", "--best", "compression/liberty.jpg"])

        # Decompress
        run(bzip2["-f", "-k", "--decompress", "compression/text.html.bz2"])
        run(bzip2["-f", "-k", "--decompress", "compression/chicken.jpg.bz2"])
        run(bzip2["-f", "-k", "--decompress", "compression/control.bz2"])
        run(bzip2["-f", "-k", "--decompress", "compression/input.source.bz2"])
        run(bzip2["-f", "-k", "--decompress", "compression/liberty.jpg.bz2"])
