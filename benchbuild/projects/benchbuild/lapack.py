import logging

import benchbuild as bb
from benchbuild.settings import CFG
from benchbuild.utils import download
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.settings import get_number_of_jobs


@download.with_git("https://github.com/xianyi/OpenBLAS", limit=5)
class OpenBlas(bb.Project):
    NAME = 'openblas'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'OpenBLAS'
    VERSION = 'HEAD'

    def compile(self):
        self.download()

        with bb.cwd(self.src_file):
            clang = bb.compiler.cc(self)
            _make = bb.watch(make)
            _make("CC=" + str(clang))

    def run_tests(self):
        log = logging.getLogger(__name__)
        log.warning('Not implemented')


@download.with_wget({"3.2.1": "http://www.netlib.org/clapack/clapack.tgz"})
class Lapack(bb.Project):
    NAME = 'lapack'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    VERSION = '3.2.1'
    SRC_FILE = "clapack.tgz"

    def compile(self):
        self.download()
        tar("xfz", self.src_file)
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

            with bb.cwd(bb.path("BLAS") / "TESTING"):
                _make("-j", get_number_of_jobs(CFG), "f2clib", "blaslib")
                _make("-j", get_number_of_jobs(CFG), "-f", "Makeblat2")
                _make("-j", get_number_of_jobs(CFG), "-f", "Makeblat3")
            _make = bb.watch(make)

    def run_tests(self):
        unpack_dir = bb.path("CLAPACK-{0}".format(self.version))
        with bb.cwd(unpack_dir / "BLAS"):
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
