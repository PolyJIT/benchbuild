import logging
from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import Git, Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class OpenBlas(Project):
    NAME = 'openblas'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'OpenBLAS'

    src_uri = "https://github.com/xianyi/" + SRC_FILE

    def download(self):
        Git(self.src_uri, self.SRC_FILE)

    def configure(self):
        pass

    def build(self):
        clang = cc(self)
        with local.cwd(self.SRC_FILE):
            run(make["CC=" + str(clang)])

    def run_tests(self, runner):
        del runner
        log = logging.getLogger(__name__)
        log.warning('Not implemented')


class Lapack(Project):
    NAME = 'lapack'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    VERSION = '3.2.1'
    SRC_FILE = "clapack.tgz"

    src_dir = "CLAPACK-{0}".format(VERSION)
    src_uri = "http://www.netlib.org/clapack/clapack.tgz"

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xfz", self.SRC_FILE)

    def configure(self):
        clang = cc(self)
        clang_cxx = cxx(self)
        with local.cwd(self.src_dir):
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

    def build(self):
        with local.cwd(self.src_dir):
            run(make["-j", CFG["jobs"], "f2clib", "blaslib"])
            with local.cwd(path.join("BLAS", "TESTING")):
                run(make["-j", CFG["jobs"], "-f", "Makeblat2"])
                run(make["-j", CFG["jobs"], "-f", "Makeblat3"])

    def run_tests(self, runner):
        with local.cwd(self.src_dir):
            with local.cwd(path.join("BLAS")):
                xblat2s = wrap("xblat2s", self)
                xblat2d = wrap("xblat2d", self)
                xblat2c = wrap("xblat2c", self)
                xblat2z = wrap("xblat2z", self)

                xblat3s = wrap("xblat3s", self)
                xblat3d = wrap("xblat3d", self)
                xblat3c = wrap("xblat3c", self)
                xblat3z = wrap("xblat3z", self)

                runner((xblat2s < "sblat2.in"))
                runner((xblat2d < "dblat2.in"))
                runner((xblat2c < "cblat2.in"))
                runner((xblat2z < "zblat2.in"))
                runner((xblat3s < "sblat3.in"))
                runner((xblat3d < "dblat3.in"))
                runner((xblat3c < "cblat3.in"))
                runner((xblat3z < "zblat3.in"))
