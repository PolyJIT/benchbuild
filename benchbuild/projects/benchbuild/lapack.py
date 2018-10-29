import logging

from plumbum import local

from benchbuild import project
from benchbuild.settings import CFG
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make, tar


@download.with_git("https://github.com/xianyi/OpenBLAS", limit=5)
class OpenBlas(project.Project):
    NAME = 'openblas'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'OpenBLAS'
    VERSION = 'HEAD'

    def compile(self):
        self.download()

        clang = compiler.cc(self)
        with local.cwd(self.src_file):
            run.run(make["CC=" + str(clang)])

    def run_tests(self, runner):
        del runner
        log = logging.getLogger(__name__)
        log.warning('Not implemented')


@download.with_wget({"3.2.1": "http://www.netlib.org/clapack/clapack.tgz"})
class Lapack(project.Project):
    NAME = 'lapack'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    VERSION = '3.2.1'
    SRC_FILE = "clapack.tgz"

    def compile(self):
        self.download()
        tar("xfz", self.src_file)
        unpack_dir = "CLAPACK-{0}".format(self.version)

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)
        with local.cwd(unpack_dir):
            with open("make.inc", 'w') as makefile:
                content = [
                    "SHELL     = /bin/sh\n", "PLAT      = _LINUX\n",
                    "CC        = " + str(clang) + "\n",
                    "CXX       = " + str(clang_cxx) + "\n",
                    "CFLAGS    = -I$(TOPDIR)/INCLUDE\n",
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

            run.run(make["-j", CFG["jobs"], "f2clib", "blaslib"])
            with local.cwd(local.path("BLAS") / "TESTING"):
                run.run(make["-j", CFG["jobs"], "-f", "Makeblat2"])
                run.run(make["-j", CFG["jobs"], "-f", "Makeblat3"])

    def run_tests(self, runner):
        unpack_dir = local.path("CLAPACK-{0}".format(self.version))
        with local.cwd(unpack_dir / "BLAS"):
            xblat2s = wrapping.wrap("xblat2s", self)
            xblat2d = wrapping.wrap("xblat2d", self)
            xblat2c = wrapping.wrap("xblat2c", self)
            xblat2z = wrapping.wrap("xblat2z", self)

            xblat3s = wrapping.wrap("xblat3s", self)
            xblat3d = wrapping.wrap("xblat3d", self)
            xblat3c = wrapping.wrap("xblat3c", self)
            xblat3z = wrapping.wrap("xblat3z", self)

            runner((xblat2s < "sblat2.in"))
            runner((xblat2d < "dblat2.in"))
            runner((xblat2c < "cblat2.in"))
            runner((xblat2z < "zblat2.in"))
            runner((xblat3s < "sblat3.in"))
            runner((xblat3d < "dblat3.in"))
            runner((xblat3c < "cblat3.in"))
            runner((xblat3z < "zblat3.in"))
