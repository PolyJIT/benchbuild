#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import Project, ProjectFactory
from pprof.settings import config

from os import path
from plumbum import local


class PolyBenchGroup(Project):

    path_dict = {
        "correlation": "datamining",
        "covariance": "datamining",

        "2mm": "linear-algebra/kernels",
        "3mm": "linear-algebra/kernels",
        "atax": "linear-algebra/kernels",
        "bicg": "linear-algebra/kernels",
        "doitgen": "linear-algebra/kernels",
        "mvt": "linear-algebra/kernels",

        "cholesky": "linear-algebra/solvers",
        "durbin": "linear-algebra/solvers",
        "lu": "linear-algebra/solvers",
        "ludcmp": "linear-algebra/solvers",
        "gramschmidt": "linear-algebra/solvers",
        "trisolv": "linear-algebra/solvers",

        "gemm": "linear-algebra/blas",
        "gemver": "linear-algebra/blas",
        "gesummv": "linear-algebra/blas",
        "symm": "linear-algebra/blas",
        "syr2k": "linear-algebra/blas",
        "syrk": "linear-algebra/blas",
        "trmm": "linear-algebra/blas",

        "adi": "stencils",
        "fdtd-2d": "stencils",
        "heat-3d": "stencils",
        "jacobi-1d": "stencils",
        "jacobi-2d": "stencils",
        "seidel-2d": "stencils",

        "nussinov": "medley",
        "deriche": "medley",
        "floyd-warshall": "medley",
    }

    def __init__(self, exp, name):
        super(PolyBenchGroup, self).__init__(
            exp, name, "polybench", "polybench")
        self.sourcedir = path.join(config["sourcedir"],
                                   "polybench", self.path_dict[name], name)
        self.setup_derived_filenames()

    src_dir = "polybench-c-4.1"
    src_file = src_dir + ".tar.gz"
    src_uri = "http://downloads.sourceforge.net/project/polybench/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar
        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfz', path.join(self.builddir, self.src_file))

    def configure(self):
        from plumbum.cmd import cp
        with local.cwd(self.builddir):
            cp("-ar", path.join(self.src_dir, self.path_dict[self.name],
                                self.name), self.name + ".dir")
            cp("-ar", path.join(self.src_dir, "utilities"), ".")

    def build(self):
        from pprof.utils.compiler import lt_clang

        src_file = path.join(self.name + ".dir", self.name + ".c")
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags)
            clang("-I", "utilities",
                  "-I", self.name,
                  "-DPOLYBENCH_USE_C99_PROTO",
                  "utilities/polybench.c", src_file,
                  "-lm",
                  "-o", self.run_f)


# Datamining

class Correlation(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Correlation(exp, "correlation")
    ProjectFactory.addFactory("Correlation", Factory())


class Covariance(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Covariance(exp, "covariance")
    ProjectFactory.addFactory("Covariance", Factory())

# Linear Algebra / Kernels

class TwoMM(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return TwoMM(exp, "2mm")
    ProjectFactory.addFactory("TwoMM", Factory())


class ThreeMM(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return ThreeMM(exp, "3mm")
    ProjectFactory.addFactory("ThreeMM", Factory())


class Atax(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Atax(exp, "atax")
    ProjectFactory.addFactory("Atax", Factory())


class BicG(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return BicG(exp, "bicg")
    ProjectFactory.addFactory("BicG", Factory())


class Doitgen(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Doitgen(exp, "doitgen")
    ProjectFactory.addFactory("Doitgen", Factory())


class Mvt(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Mvt(exp, "mvt")
    ProjectFactory.addFactory("Mvt", Factory())


# Linear Algebra / Blas

class Gemm(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Gemm(exp, "gemm")
    ProjectFactory.addFactory("Gemm", Factory())


class Gemver(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Gemver(exp, "gemver")
    ProjectFactory.addFactory("Gemver", Factory())


class Gesummv(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Gesummv(exp, "gesummv")
    ProjectFactory.addFactory("Gesummv", Factory())


class Symm(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Symm(exp, "symm")
    ProjectFactory.addFactory("Symm", Factory())


class Syr2k(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Syr2k(exp, "syr2k")
    ProjectFactory.addFactory("Syr2k", Factory())


class Syrk(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Syrk(exp, "syrk")
    ProjectFactory.addFactory("Syrk", Factory())


class Trmm(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Trmm(exp, "trmm")
    ProjectFactory.addFactory("Trmm", Factory())

# Linear Algebra / Solvers

class Cholesky(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Cholesky(exp, "cholesky")
    ProjectFactory.addFactory("Cholesky", Factory())


class Durbin(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Durbin(exp, "durbin")
    ProjectFactory.addFactory("Durbin", Factory())


class Gramschmidt(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Gramschmidt(exp, "gramschmidt")
    ProjectFactory.addFactory("Gramschmidt", Factory())


class Lu(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Lu(exp, "lu")
    ProjectFactory.addFactory("Lu", Factory())


class LuDCMP(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return LuDCMP(exp, "ludcmp")
    ProjectFactory.addFactory("LuDCMP", Factory())


class Trisolv(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Trisolv(exp, "trisolv")
    ProjectFactory.addFactory("Trisolv", Factory())


# Medley


class Deriche(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Deriche(exp, "deriche")
    ProjectFactory.addFactory("Deriche", Factory())


class FloydWarshall(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return FloydWarshall(exp, "floyd-warshall")
    ProjectFactory.addFactory("FloydWarshall", Factory())


class Nussinov(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Nussinov(exp, "nussinov")
    ProjectFactory.addFactory("Nussinov", Factory())


# Stencils

class Adi(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Adi(exp, "adi")
    ProjectFactory.addFactory("Adi", Factory())


class FDTD2D(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return FDTD2D(exp, "fdtd-2d")
    ProjectFactory.addFactory("FDTD2D", Factory())


class Jacobi1D(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Jacobi1D(exp, "jacobi-1d")
    ProjectFactory.addFactory("Jacobi1D", Factory())


class Jacobi2Dimper(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Jacobi2Dimper(exp, "jacobi-2d")
    ProjectFactory.addFactory("Jacobi2D", Factory())


class Seidel2D(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Seidel2D(exp, "seidel-2d")
    ProjectFactory.addFactory("Seidel2D", Factory())


class Heat3D(PolyBenchGroup):

    class Factory:

        def create(self, exp):
            return Heat3D(exp, "heat-3d")
    ProjectFactory.addFactory("heat-3d", Factory())
