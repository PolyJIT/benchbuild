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
        self.testdir = path.join(config["testdir"],self.domain, "lapack", "tests")

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
        from pprof.project import clang
        with local.cwd(lapack_dir):
            with open("make.inc", 'w') as Makefile:
                content = [
                "SHELL     = /bin/sh\n",
                "PLAT      = _LINUX\n",
                "CC        = " + str(clang()) + "\n",
                "CFLAGS    = -I$(TOPDIR)/INCLUDE " + " ".join(self.cflags) + "\n",
                "LOADER    = " + str(clang()) + "\n",
                "LOADOPTS  = " + " ".join(self.ldflags) + "\n",
                "NOOPT     = -O0 -I$(TOPDIR)/INCLUDE " + " ".join(self.cflags) + "\n",
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
            make["-j" + config["jobs"], "f2clib", "lapack_install", "lib"] & FG
            make["-i", "lapack_testing", "blas_testing"] & FG


    class Factory:
        def create(self, exp):
            return Lapack(exp, "lapack")
    ProjectFactory.addFactory("Lapack", Factory())


class Xlintstc(Lapack):

    """ lapack/xlintstc benchmark """

    tests = ["ctest.in"]

    class Factory:
        def create(self, exp):
            return Xlintstc(exp, "xlintstc")
    ProjectFactory.addFactory("Xlintstc", Factory())


class Xlintstd(Lapack):

    """ lapack/xlintstd benchmark """

    tests = ["dtest.in"]

    class Factory:
        def create(self, exp):
            return Xlintstd(exp, "xlintstd")
    ProjectFactory.addFactory("Xlintstd", Factory())


class Xlintstds(Lapack):

    """ lapack/xlintstds benchmark """

    tests = ["dstest.in"]

    class Factory:
        def create(self, exp):
            return Xlintstds(exp, "xlintstds")
    ProjectFactory.addFactory("Xlintstds", Factory())


class Xlintstrfc(Lapack):

    """ lapack/xlintstfrfc benchmark """

    tests = ["ctest_rfp.in"]

    class Factory:
        def create(self, exp):
            return Xlintstrfc(exp, "xlintstrfc")
    ProjectFactory.addFactory("Xlintstrfc", Factory())


class Xlintstrfd(Lapack):

    """ lapack/xlintstfrfd benchmark """

    tests = ["dtest_rfp.in"]

    class Factory:
        def create(self, exp):
            return Xlintstrfc(exp, "xlintstrfd")
    ProjectFactory.addFactory("Xlintstrfd", Factory())


class Xlintstrfs(Lapack):

    """ lapack/xlintstfrfs benchmark """

    tests = ["stest_rfp.in"]

    class Factory:
        def create(self, exp):
            return Xlintstrfs(exp, "xlintstrfs")
    ProjectFactory.addFactory("Xlintstrfs", Factory())


class Xlintstrfz(Lapack):

    """ lapack/xlintstfrfz benchmark """

    tests = ["ztest_rfp.in"]

    class Factory:
        def create(self, exp):
            return Xlintstrfz(exp, "xlintstrfz")
    ProjectFactory.addFactory("Xlintstrfz", Factory())


class Xlintsts(Lapack):

    """ lapack/xlintsts benchmark """

    tests = ["stest.in"]

    class Factory:
        def create(self, exp):
            return Xlintsts(exp, "xlintsts")
    ProjectFactory.addFactory("Xlintsts", Factory())


class Xlintstz(Lapack):

    """ lapack/xlintstz benchmark """

    tests = ["ztest.in"]

    class Factory:
        def create(self, exp):
            return Xlintstz(exp, "xlintstz")
    ProjectFactory.addFactory("Xlintstz", Factory())


class Xlintstzc(Lapack):

    """ lapack/xlintstzc benchmark """

    tests = ["zctest.in"]

    class Factory:
        def create(self, exp):
            return Xlintstzc(exp, "xlintstzc")
    ProjectFactory.addFactory("Xlintstzc", Factory())
