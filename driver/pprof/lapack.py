from project import *
from os import path

from settings import config

class Lapack(Project):
    domain = "scientific"

    def __init__(self, exp, name):
        super(Lapack, self).__init__(exp, name, self.domain)
        self.sourcedir = path.join(config["sourcedir"], "src", "lapack", name)
        self.testdir = path.join(config["testdir"],self.domain, "lapack", "tests")

        self.setup_derived_filenames()
        self.tests = []

    def run(self, experiment):
        tests = [path.join(self.testdir, x) for x in self.tests]
        with local.cwd(self.builddir):
            for test in tests:
                (experiment < test) & FG


class Eigen(Lapack):
    tests = [
        "nep.in", "sep.in", "svd.in", "cec.in", "ced.in", "cgg.in",
        "cgd.in", "csb.in", "csg.in", "cbal.in", "cbak.in", "cgbal.in",
        "cgbak.in", "cbb.in", "glm.in", "gqr.in", "gsv.in", "csd.in",
        "lse.in"
    ]

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
