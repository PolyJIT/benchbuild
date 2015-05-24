from os import path

from group import PprofGroup
from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from plumbum import FG, local
from os import path


class Lapack(PprofGroup):
    domain = "scientific"

    def __init__(self, exp, name):
        super(Lapack, self).__init__(exp, name, self.domain)
        self.sourcedir = path.join(config["sourcedir"], "src", "lapack", name)
        self.testdir = path.join(
            config["testdir"], self.domain, "lapack", "tests")

        self.setup_derived_filenames()
        self.tests = []

    src_dir = "CLAPACK-3.2.1"
    src_file = "clapack.tgz"
    src_uri = "http://www.netlib.org/clapack/clapack.tgz"

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar("xfz", self.src_file)

    def configure(self):
        lapack_dir = path.join(self.builddir, self.src_dir)
        from pprof.utils.compiler import clang
        with local.cwd(lapack_dir):
            with open("make.inc", 'w') as Makefile:
                content = [
                    "SHELL     = /bin/sh\n",
                    "PLAT      = _LINUX\n",
                    "CC        = " + str(clang()) + "\n",
                    "CFLAGS    = -I$(TOPDIR)/INCLUDE " +
                    " ".join(self.cflags) + "\n",
                    "LOADER    = " + str(clang()) + "\n",
                    "LOADOPTS  = " + " ".join(self.ldflags) + "\n",
                    "NOOPT     = -O0 -I$(TOPDIR)/INCLUDE " +
                    " ".join(self.cflags) + "\n",
                    "DRVCFLAGS = $(CFLAGS) " + " ".join(self.cflags) + "\n",
                    "F2CCFLAGS = $(CFLAGS) " + " ".join(self.cflags) + "\n",
                    "TIMER     = INT_CPU_TIME\n",
                    "ARCH      = ar\n",
                    "ARCHFLAGS = cr\n",
                    "RANLIB    = ranlib\n",
                    "BLASLIB   = ../../blas$(PLAT).a\n",
                    "XBLASLIB  = \n",
                    "LAPACKLIB = lapack$(PLAT).a\n",
                    "F2CLIB    = ../../F2CLIBS/libf2c.a\n",
                    "TMGLIB    = tmglib$(PLAT).a\n",
                    "EIGSRCLIB = eigsrc$(PLAT).a\n",
                    "LINSRCLIB = linsrc$(PLAT).a\n",
                    "F2CLIB    = ../../F2CLIBS/libf2c.a\n"
                ]
                Makefile.writelines(content)

    def build(self):
        from plumbum.cmd import make
        lapack_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(lapack_dir):
            make["-j" + config["jobs"], "clean",
                 "f2clib", "lapack_install", "lib"] & FG

    def run_tests(self, experiment):
        pass

    class Factory:

        def create(self, exp):
            return Lapack(exp, "lapack")
    ProjectFactory.addFactory("Lapack", Factory())
