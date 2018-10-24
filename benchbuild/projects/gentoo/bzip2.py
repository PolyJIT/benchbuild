"""
bzip2 experiment within gentoo chroot.
"""
from plumbum import local

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils import download, wrapping
from benchbuild.utils.cmd import tar


class BZip2(GentooGroup):
    """
        app-arch/bzip2
    """
    NAME = "bzip2"
    DOMAIN = "app-arch"

    test_url = "http://lairosiel.de/dist/"
    test_archive = "compression.tar.gz"
    testfiles = [
        "text.html", "chicken.jpg", "control", "input.source", "liberty.jpg"
    ]

    def compile(self):
        super(BZip2, self).compile()

        test_archive = self.test_archive
        test_url = self.test_url + test_archive
        download.Wget(test_url, test_archive)
        tar("fxz", test_archive)

    def run_tests(self, runner):
        bzip2 = wrapping.wrap(local.path('/bin/bzip2'), self)

        # Compress
        runner(bzip2["-f", "-z", "-k", "--best", "compression/text.html"])
        runner(bzip2["-f", "-z", "-k", "--best", "compression/chicken.jpg"])
        runner(bzip2["-f", "-z", "-k", "--best", "compression/control"])
        runner(bzip2["-f", "-z", "-k", "--best", "compression/input.source"])
        runner(bzip2["-f", "-z", "-k", "--best", "compression/liberty.jpg"])

        # Decompress
        runner(bzip2["-f", "-k", "--decompress", "compression/text.html.bz2"])
        runner(
            bzip2["-f", "-k", "--decompress", "compression/chicken.jpg.bz2"])
        runner(bzip2["-f", "-k", "--decompress", "compression/control.bz2"])
        runner(
            bzip2["-f", "-k", "--decompress", "compression/input.source.bz2"])
        runner(
            bzip2["-f", "-k", "--decompress", "compression/liberty.jpg.bz2"])
