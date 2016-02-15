"""
bzip2 experiment within gentoo chroot.
"""
from os import path
from pprof.projects.gentoo.gentoo import GentooGroup
from pprof.utils.downloader import Wget
from pprof.utils.run import run, uchroot
from plumbum import local
from plumbum.cmd import tar  # pylint: disable=E0401


class BZip2(GentooGroup):
    """
        app-arch/bzip2
    """
    NAME = "gentoo-bzip2"
    DOMAIN = "app-arch"

    test_url = "http://lairosiel.de/dist/"
    test_archive = "compression.tar.gz"
    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    def prepare(self):
        super(BZip2, self).prepare()

        test_archive = self.test_archive
        test_url = self.test_url + test_archive
        with local.cwd(self.builddir):
            Wget(test_url, test_archive)
            tar("fxz", test_archive)

    def build(self):
        with local.cwd(self.builddir):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            run(emerge_in_chroot["app-arch/bzip2"])

    def run_tests(self, experiment):
        from pprof.project import wrap

        wrap(path.join(self.builddir, "bin", "bzip2"), experiment,
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
