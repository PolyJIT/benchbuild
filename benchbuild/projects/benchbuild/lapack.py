from os import path
import logging

from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.settings import CFG
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Git, Wget
from benchbuild.utils.run import run
from benchbuild.utils.cmd import make, tar
from plumbum import local


class OpenBlas(BenchBuildGroup):
    NAME = 'openblas'
    DOMAIN = 'scientific'
    SRC_FILE = 'OpenBLAS'

    src_uri = "https://github.com/xianyi/" + SRC_FILE

    def download(self):
        Git(self.src_uri, self.SRC_FILE)

    def configure(self):
        pass

    def build(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        with local.cwd(self.SRC_FILE):
            run(make["CC=" + str(clang)])

    def run_tests(self, experiment, run):
        log = logging.getLogger(__name__)
        log.warn('Not implemented')


class Lapack(BenchBuildGroup):
    NAME = 'lapack'
    DOMAIN = 'scientific'
    VERSION = '3.2.1'
    SRC_FILE = "clapack.tgz"

    def __init__(self, exp):
        super(Lapack, self).__init__(exp)
        self.sourcedir = path.join(
            str(CFG["src_dir"]), "src", "lapack", self.name)
        self.testdir = path.join(
            str(CFG["test_dir"]), self.domain, "lapack", "tests")

        self.setup_derived_filenames()
        self.tests = []

    src_dir = "CLAPACK-{0}".format(VERSION)
    src_uri = "http://www.netlib.org/clapack/clapack.tgz"

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xfz", self.SRC_FILE)

    def configure(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)
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

    def run_tests(self, experiment, run):
        with local.cwd(self.src_dir):
            with local.cwd(path.join("BLAS")):
                xblat2s = wrap("xblat2s", experiment)
                xblat2d = wrap("xblat2d", experiment)
                xblat2c = wrap("xblat2c", experiment)
                xblat2z = wrap("xblat2z", experiment)

                xblat3s = wrap("xblat3s", experiment)
                xblat3d = wrap("xblat3d", experiment)
                xblat3c = wrap("xblat3c", experiment)
                xblat3z = wrap("xblat3z", experiment)

                run((xblat2s < "sblat2.in"))
                run((xblat2d < "dblat2.in"))
                run((xblat2c < "cblat2.in"))
                run((xblat2z < "zblat2.in"))
                run((xblat3s < "sblat3.in"))
                run((xblat3d < "dblat3.in"))
                run((xblat3c < "cblat3.in"))
                run((xblat3z < "zblat3.in"))
