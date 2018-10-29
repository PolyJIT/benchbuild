"""
gzip experiment within gentoo chroot.
"""
from plumbum import local

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils import download, wrapping
from benchbuild.utils.cmd import tar


class GZip(GentooGroup):
    """
        app-arch/gzip
    """
    NAME = "gzip"
    DOMAIN = "app-arch"

    test_url = "http://lairosiel.de/dist/"
    test_archive = "compression.tar.gz"
    testfiles = [
        "text.html", "chicken.jpg", "control", "input.source", "liberty.jpg"
    ]

    def compile(self):
        super(GZip, self).compile()

        test_archive = self.test_archive
        test_url = self.test_url + test_archive
        download.Wget(test_url, test_archive)
        tar("fxz", test_archive)

    def run_tests(self, runner):
        gzip = wrapping.wrap(local.path('/bin/gzip'), self)

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
