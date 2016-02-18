"""
LAMMPS (sci-physics/lammps) project within gentoo chroot.
"""
from os import path
from glob import glob
from pprof.projects.gentoo.gentoo import GentooGroup
from pprof.utils.downloader import Wget
from pprof.utils.run import run, uchroot
from plumbum import local
from plumbum.cmd import tar # pylint: disable=E0401


class Lammps(GentooGroup):
    """
        sci-physics/lammps
    """
    NAME = "gentoo-lammps"
    DOMAIN = "sci-physics"

    test_url = "http://lairosiel.de/dist/"
    test_archive = "lammps.tar.gz"

    def prepare(self):
        super(Lammps, self).prepare()

        test_archive = self.test_archive
        test_url = self.test_url + test_archive
        with local.cwd(self.builddir):
            Wget(test_url, test_archive)
            tar("fxz", test_archive)

    def build(self):
        with local.cwd(self.builddir):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            with local.env(USE="-mpi -doc"):
                run(emerge_in_chroot["sci-physics/lammps"])

    def run_tests(self, experiment):
        from pprof.project import wrap, strip_path_prefix

        wrap(path.join(self.builddir, "usr/bin/lmp_serial"), experiment,
             self.builddir)
        lammps = uchroot()["/usr/bin/lmp_serial"]
        lammps_dir = path.join(self.builddir, "lammps")

        with local.cwd(path.join(self.builddir, "lammps")):
            tests = glob(path.join(lammps_dir, "in.*"))
            for test in tests:
                run((lammps < strip_path_prefix(test, self.builddir)))

