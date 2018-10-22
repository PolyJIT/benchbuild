"""
LAMMPS (sci-physics/lammps) project within gentoo chroot.
"""
from plumbum import local

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.cmd import tar
from benchbuild.utils.downloader import Wget
from benchbuild.utils.wrapping import wrap, strip_path_prefix


class Lammps(GentooGroup):
    """
        sci-physics/lammps
    """
    NAME = "lammps"
    DOMAIN = "sci-physics"

    test_url = "http://lairosiel.de/dist/"
    test_archive = "lammps.tar.gz"

    def compile(self):
        self.emerge_env = dict(USE="-mpi -doc")

        super(Lammps, self).compile()

        test_archive = self.test_archive
        test_url = self.test_url + test_archive
        Wget(test_url, test_archive)
        tar("fxz", test_archive)

    def run_tests(self, runner):
        builddir = self.builddir
        lammps = wrap(local.path('/') / 'usr' / 'bin' / 'lmp_serial', self)
        lammps_dir = builddir / "lammps"

        with local.cwd(lammps_dir):
            tests = lammps_dir // "in.*"
            for test in tests:
                runner((lammps < strip_path_prefix(test, builddir)))
