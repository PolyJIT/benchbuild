"""
bzip2 experiment within gentoo chroot.
"""
from plumbum import local

import benchbuild as bb
from benchbuild.projects.gentoo.gentoo import GentooGroup
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
        super().compile()

        test_archive = self.test_archive
        test_url = self.test_url + test_archive
        bb.download.Wget(test_url, test_archive)
        tar("fxz", test_archive)

    def run_tests(self):
        bzip2 = bb.wrap(local.path('/bin/bzip2'), self)
        bzip2 = bb.watch(bzip2)

        # Compress
        bzip2("-f", "-z", "-k", "--best", "compression/text.html")
        bzip2("-f", "-z", "-k", "--best", "compression/chicken.jpg")
        bzip2("-f", "-z", "-k", "--best", "compression/control")
        bzip2("-f", "-z", "-k", "--best", "compression/input.source")
        bzip2("-f", "-z", "-k", "--best", "compression/liberty.jpg")

        # Decompress
        bzip2("-f", "-k", "--decompress", "compression/text.html.bz2")
        bzip2("-f", "-k", "--decompress", "compression/chicken.jpg.bz2")
        bzip2("-f", "-k", "--decompress", "compression/control.bz2")
        bzip2("-f", "-k", "--decompress", "compression/input.source.bz2")
        bzip2("-f", "-k", "--decompress", "compression/liberty.jpg.bz2")
