import logging

from plumbum import local

from benchbuild import project
from benchbuild.downloads import Git, HTTP
from benchbuild.settings import CFG
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import make, tar


class OpenBlas(project.Project):
    NAME = 'openblas'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    VERSION = 'HEAD'
    SOURCE = [
        Git(remote='https://github.com/xianyi/OpenBLAS',
            local='OpenBLAS',
            limit=5,
            refspec='HEAD')
    ]

    def compile(self):
        openblas_repo = local.path(self.source[0].local)
        clang = compiler.cc(self)
        with local.cwd(openblas_repo):
            make_ = run.watch(make)
            make_("CC=" + str(clang))

    def run_tests(self):
        log = logging.getLogger(__name__)
        log.warning('Not implemented')


class Lapack(project.Project):
    NAME = 'lapack'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    VERSION = '3.2.1'
    SOURCE = [
        HTTP(remote={'3.2.1': 'http://www.netlib.org/clapack/clapack.tgz'},
             local='clapack.tgz')
    ]

    def compile(self):
        clapack_source = local.path(self.source[0].local)

        tar("xfz", clapack_source)
        unpack_dir = "CLAPACK-{0}".format(self.version)

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)
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

            make_ = run.watch(make)
            make_("-j", CFG["jobs"], "f2clib", "blaslib")
            with local.cwd(local.path("BLAS") / "TESTING"):
                make_("-j", CFG["jobs"], "-f", "Makeblat2")
                make_("-j", CFG["jobs"], "-f", "Makeblat3")

    def run_tests(self):
        unpack_dir = local.path("CLAPACK-{0}".format(self.version))
        with local.cwd(unpack_dir / "BLAS"):
            xblat2s = wrapping.wrap("xblat2s", self)
            xblat2s = run.watch((xblat2s < "sblat2.in"))
            xblat2s()

            xblat2d = wrapping.wrap("xblat2d", self)
            xblat2d = run.watch((xblat2d < "dblat2.in"))
            xblat2d()

            xblat2c = wrapping.wrap("xblat2c", self)
            xblat2c = run.watch((xblat2c < "cblat2.in"))
            xblat2c()

            xblat2z = wrapping.wrap("xblat2z", self)
            xblat2z = run.watch((xblat2z < "zblat2.in"))
            xblat2z()

            xblat3s = wrapping.wrap("xblat3s", self)
            xblat3s = run.watch((xblat3s < "sblat3.in"))
            xblat3s()

            xblat3d = wrapping.wrap("xblat3d", self)
            xblat3d = run.watch((xblat3d < "dblat3.in"))
            xblat3d()

            xblat3c = wrapping.wrap("xblat3c", self)
            xblat3c = run.watch((xblat3c < "cblat3.in"))
            xblat3c()

            xblat3z = wrapping.wrap("xblat3z", self)
            xblat3z = run.watch((xblat3z < "zblat3.in"))
            xblat3z()
