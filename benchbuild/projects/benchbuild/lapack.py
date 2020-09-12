import logging

from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.settings import CFG
from benchbuild.source import HTTP, Git
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.settings import get_number_of_jobs


class OpenBlas(bb.Project):
    NAME = 'openblas'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SOURCE = [
        Git(
            remote='https://github.com/xianyi/OpenBLAS',
            local='OpenBLAS',
            limit=5,
            refspec='HEAD'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        openblas_repo = local.path(self.source_of('OpenBLAS'))
        clang = bb.compiler.cc(self)
        with local.cwd(openblas_repo):
            _make = bb.watch(make)
            _make("CC=" + str(clang))

    def run_tests(self):
        log = logging.getLogger(__name__)
        log.warning('Not implemented')


class Lapack(bb.Project):
    NAME = 'lapack'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SOURCE = [
        HTTP(
            remote={'3.2.1': 'http://www.netlib.org/clapack/clapack.tgz'},
            local='clapack.tgz'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        clapack_source = local.path(self.source_of('clapack.tgz'))
        clapack_version = self.version_of('clapack.tgz')

        tar("xfz", clapack_source)
        unpack_dir = "CLAPACK-{0}".format(clapack_version)

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)
        with local.cwd(unpack_dir):
            with open("make.inc", 'w') as makefile:
                content = [
                    "SHELL     = /bin/sh\n", "PLAT      = _LINUX\n",
                    "CC        = " + str(clang) + "\n", "CXX       = " +
                    str(clang_cxx) + "\n", "CFLAGS    = -I$(TOPDIR)/INCLUDE\n",
                    "LOADER    = " + str(clang) + "\n", "LOADOPTS  = \n",
                    "NOOPT     = -O0 -I$(TOPDIR)/INCLUDE\n",
                    "DRVCFLAGS = $(CFLAGS)\n", "F2CCFLAGS = $(CFLAGS)\n",
                    "TIMER     = INT_CPU_TIME\n", "ARCH      = ar\n",
                    "ARCHFLAGS = cr\n", "RANLIB    = ranlib\n",
                    "BLASLIB   = ../../blas$(PLAT).a\n", "XBLASLIB  = \n",
                    "LAPACKLIB = lapack$(PLAT).a\n",
                    "F2CLIB    = ../../F2CLIBS/libf2c.a\n",
                    "TMGLIB    = tmglib$(PLAT).a\n",
                    "EIGSRCLIB = eigsrc$(PLAT).a\n",
                    "LINSRCLIB = linsrc$(PLAT).a\n",
                    "F2CLIB    = ../../F2CLIBS/libf2c.a\n"
                ]
                makefile.writelines(content)

            _make = bb.watch(make)
            _make("-j", get_number_of_jobs(CFG), "f2clib", "blaslib")
            with local.cwd(local.path("BLAS") / "TESTING"):
                _make("-j", get_number_of_jobs(CFG), "-f", "Makeblat2")
                _make("-j", get_number_of_jobs(CFG), "-f", "Makeblat3")

    def run_tests(self):
        clapack_version = self.version_of('clapack.tgz')
        unpack_dir = local.path("CLAPACK-{0}".format(clapack_version))
        with local.cwd(unpack_dir / "BLAS"):
            xblat2s = bb.wrap("xblat2s", self)
            _xblat2s = bb.watch((xblat2s < "sblat2.in"))
            _xblat2s()

            xblat2d = bb.wrap("xblat2d", self)
            _xblat2d = bb.watch((xblat2d < "dblat2.in"))
            _xblat2d()

            xblat2c = bb.wrap("xblat2c", self)
            _xblat2c = bb.watch((xblat2c < "cblat2.in"))
            _xblat2c()

            xblat2z = bb.wrap("xblat2z", self)
            _xblat2z = bb.watch((xblat2z < "zblat2.in"))
            _xblat2z()

            xblat3s = bb.wrap("xblat3s", self)
            _xblat3s = bb.watch((xblat3s < "sblat3.in"))
            _xblat3s()

            xblat3d = bb.wrap("xblat3d", self)
            _xblat3d = bb.watch((xblat3d < "dblat3.in"))
            _xblat3d()

            xblat3c = bb.wrap("xblat3c", self)
            _xblat3c = bb.watch((xblat3c < "cblat3.in"))
            _xblat3c()

            xblat3z = bb.wrap("xblat3z", self)
            _xblat3z = bb.watch((xblat3z < "zblat3.in"))
            _xblat3z()
