"""
xz experiment within gentoo chroot.
"""
from plumbum import local

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils import download, run, wrapping
from benchbuild.utils.cmd import tar


class XZ(GentooGroup):
    """
        app-arch/xz
    """
    NAME = "xz"
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
        download.Wget(test_url, test_archive)
        tar("fxz", test_archive)

    def run_tests(self):
        xz = wrapping.wrap(local.path("/usr/bin/xz"), self)
        _xz = run.watch(xz)

        # Compress
        _xz("--compress", "-f", "-k", "-e", "-9", "compression/text.html")
        _xz("--compress", "-f", "-k", "-e", "-9", "compression/chicken.jpg")
        _xz("--compress", "-f", "-k", "-e", "-9", "compression/control")
        _xz("--compress", "-f", "-k", "-e", "-9", "compression/input.source")
        _xz("--compress", "-f", "-k", "-e", "-9", "compression/liberty.jpg")

        # Decompress
        _xz("--decompress", "-f", "-k", "compression/text.html.xz")
        _xz("--decompress", "-f", "-k", "compression/chicken.jpg.xz")
        _xz("--decompress", "-f", "-k", "compression/control.xz")
        _xz("--decompress", "-f", "-k", "compression/input.source.xz")
        _xz("--decompress", "-f", "-k", "compression/liberty.jpg.xz")
