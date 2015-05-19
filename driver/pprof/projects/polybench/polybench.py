#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import Project, ProjectFactory
from pprof.settings import config

from os import path
from plumbum import FG, local

class PolyBenchGroup(Project):

    path_dict = {
        "correlation": "datamining",
        "covariance": "datamining",
        "2mm": "linear-algebra/kernels",
        "3mm": "linear-algebra/kernels",
        "atax": "linear-algebra/kernels",
        "bicg": "linear-algebra/kernels",
        "cholesky": "linear-algebra/kernels",
        "doitgen": "linear-algebra/kernels",
        "gemm": "linear-algebra/kernels",
        "gemver": "linear-algebra/kernels",
        "gesummv": "linear-algebra/kernels",
        "mvt": "linear-algebra/kernels",
        "symm": "linear-algebra/kernels",
        "syr2k": "linear-algebra/kernels",
        "syrk": "linear-algebra/kernels",
        "trisolv": "linear-algebra/kernels",
        "trmm": "linear-algebra/kernels",
        "durbin": "linear-algebra/solvers",
        "dynprog": "linear-algebra/solvers",
        "gramschmidt": "linear-algebra/solvers",
        "lu": "linear-algebra/solvers",
        "ludcmp": "linear-algebra/solvers",
        "floyd-warshall": "medley",
        "reg_detect": "medley",
        "adi": "stencils",
        "fdtd-2d": "stencils",
        "fdtd-apml": "stencils",
        "jacobi-1d-imper": "stencils",
        "jacobi-2d-imper": "stencils",
        "seidel-2d": "stencils"
    }

    def __init__(self, exp, name):
        super(PolyBenchGroup, self).__init__(exp, name, "polybench", "polybench")
        self.sourcedir = path.join(config["sourcedir"],
                                   "polybench", self.path_dict[name], name)
        self.setup_derived_filenames()
        self.calls_f = path.join(self.builddir, "papi.calls.out")
        self.prof_f = path.join(self.builddir, "papi.profile.out")


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


class Cholesky(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Cholesky(exp, "cholesky")
    ProjectFactory.addFactory("Cholesky", Factory())


class Doitgen(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Doitgen(exp, "doitgen")
    ProjectFactory.addFactory("Doitgen", Factory())


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


class Mvt(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Mvt(exp, "mvt")
    ProjectFactory.addFactory("Mvt", Factory())


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


class Trisolv(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Trisolv(exp, "trisolv")
    ProjectFactory.addFactory("Trisolv", Factory())


class Trmm(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Trmm(exp, "trmm")
    ProjectFactory.addFactory("Trmm", Factory())


class Durbin(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Durbin(exp, "durbin")
    ProjectFactory.addFactory("Durbin", Factory())


class Dynprog(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Dynprog(exp, "dynprog")
    ProjectFactory.addFactory("Dynprog", Factory())


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


class FloydWarshall(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return FloydWarshall(exp, "floyd-warshall")
    ProjectFactory.addFactory("FloydWarshall", Factory())


class RegDetect(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return RegDetect(exp, "reg_detect")
    ProjectFactory.addFactory("RegDetect", Factory())


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


class FDTDAPML(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return FDTDAPML(exp, "fdtd-apml")
    ProjectFactory.addFactory("FDTDAPML", Factory())


class Jacobi1Dimper(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Jacobi1Dimper(exp, "jacobi-1d-imper")
    ProjectFactory.addFactory("Jacobi1Dimper", Factory())


class Jacobi2Dimper(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Jacobi2Dimper(exp, "jacobi-2d-imper")
    ProjectFactory.addFactory("Jacobi2Dimper", Factory())


class Seidel2D(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Seidel2D(exp, "seidel-2d")
    ProjectFactory.addFactory("Seidel2D", Factory())
