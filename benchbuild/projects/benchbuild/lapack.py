import logging

from plumbum import local

import benchbuild as bb

from benchbuild.downloads import Git, HTTP
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make, tar


class OpenBlas(bb.Project):
    NAME: str = 'openblas'
    DOMAIN: str = 'scientific'
    GROUP: str = 'benchbuild'
    VERSION: str = 'HEAD'
    SOURCE = [
        Git(remote='https://github.com/xianyi/OpenBLAS',
            local='OpenBLAS',
            limit=5,
            refspec='HEAD')
    ]

    def compile(self):
        openblas_repo = local.path(self.source[0].local)
        clang = bb.compiler.cc(self)
        with bb.cwd(openblas_repo):
            make_ = bb.watch(make)
            make_("CC=" + str(clang))

    def run_tests(self):
        log = logging.getLogger(__name__)
        log.warning('Not implemented')


class Lapack(bb.Project):
    NAME: str = 'lapack'
    DOMAIN: str = 'scientific'
    GROUP: str = 'benchbuild'
    VERSION: str = '3.2.1'
    SOURCE = [
        HTTP(remote={'3.2.1': 'http://www.netlib.org/clapack/clapack.tgz'},
             local='clapack.tgz')
    ]

    def compile(self):
        clapack_source = bb.path(self.source_of('clapack.tgz'))

        tar("xfz", clapack_source)
        unpack_dir = "CLAPACK-{0}".format(self.version)

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)
        with bb.cwd(unpack_dir):
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

            make_ = bb.watch(make)
            make_("-j", CFG["jobs"], "f2clib", "blaslib")
            with bb.cwd(local.path("BLAS") / "TESTING"):
                make_("-j", CFG["jobs"], "-f", "Makeblat2")
                make_("-j", CFG["jobs"], "-f", "Makeblat3")

    def run_tests(self):
        unpack_dir = bb.path("CLAPACK-{0}".format(self.version))
        with local.cwd(unpack_dir / "BLAS"):
            xblat2s = bb.wrap("xblat2s", self)
            xblat2s = bb.watch((xblat2s < "sblat2.in"))
            xblat2s()

            xblat2d = bb.wrap("xblat2d", self)
            xblat2d = bb.watch((xblat2d < "dblat2.in"))
            xblat2d()

            xblat2c = bb.wrap("xblat2c", self)
            xblat2c = bb.watch((xblat2c < "cblat2.in"))
            xblat2c()

            xblat2z = bb.wrap("xblat2z", self)
            xblat2z = bb.watch((xblat2z < "zblat2.in"))
            xblat2z()

            xblat3s = bb.wrap("xblat3s", self)
            xblat3s = bb.watch((xblat3s < "sblat3.in"))
            xblat3s()

            xblat3d = bb.wrap("xblat3d", self)
            xblat3d = bb.watch((xblat3d < "dblat3.in"))
            xblat3d()

            xblat3c = bb.wrap("xblat3c", self)
            xblat3c = bb.watch((xblat3c < "cblat3.in"))
            xblat3c()

            xblat3z = bb.wrap("xblat3z", self)
            xblat3z = bb.watch((xblat3z < "zblat3.in"))
            xblat3z()
