"""
LAMMPS (sci-physics/lammps) project within gentoo chroot.
"""
from plumbum import local

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.cmd import tar
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import uchroot, uretry
from benchbuild.utils.wrapping import wrap_in_uchroot as wrap
from benchbuild.utils.wrapping import strip_path_prefix


class Lammps(GentooGroup):
    """
        sci-physics/lammps
    """
    NAME = "gentoo-lammps"
    DOMAIN = "sci-physics"

    test_url = "http://lairosiel.de/dist/"
    test_archive = "lammps.tar.gz"

    def compile(self):
        super(Lammps, self).compile()

        test_archive = self.test_archive
        test_url = self.test_url + test_archive
        Wget(test_url, test_archive)
        tar("fxz", test_archive)

        emerge_in_chroot = uchroot()["/usr/bin/emerge"]
        with local.env(USE="-mpi -doc"):
            uretry(emerge_in_chroot["sci-physics/lammps"])

    def run_tests(self, runner):
        builddir = local.path(self.builddir)
        wrap(builddir / "usr" / "bin" / "lmp_serial", self, self.builddir)
        lammps = uchroot()["/usr/bin/lmp_serial"]
        lammps_dir = builddir / "lammps"

        with local.cwd("lammps"):
            tests = lammps_dir // "in.*"
            for test in tests:
                runner((lammps < strip_path_prefix(test, self.builddir)))
