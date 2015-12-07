from pprof.project import Project
from pprof.settings import config

from os import path
from plumbum import local


class PolyBenchGroup(Project):
    DOMAIN = 'polybench'
    GROUP = 'polybench'

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

    def __init__(self, exp):
        super(PolyBenchGroup, self).__init__(exp, "polybench")
        self.sourcedir = path.join(config["sourcedir"], "polybench",
                                   self.path_dict[self.name], self.name)
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
        from pprof.utils.run import run

        src_file = path.join(self.name + ".dir", self.name + ".c")
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
            run(clang["-I", "utilities", "-I", self.name,
                      "-DPOLYBENCH_USE_C99_PROTO", "-DEXTRALARGE_DATASET",
                      "utilities/polybench.c", src_file, "-lm", "-o",
                      self.run_f])

# Datamining


class Correlation(PolyBenchGroup):
    NAME = 'correlation'


class Covariance(PolyBenchGroup):
    NAME = 'covariance'


class TwoMM(PolyBenchGroup):
    NAME = '2mm'


class ThreeMM(PolyBenchGroup):
    NAME = '3mm'


class Atax(PolyBenchGroup):
    NAME = 'atax'


class BicG(PolyBenchGroup):
    NAME = 'bicg'


class Doitgen(PolyBenchGroup):
    NAME = 'doitgen'


class Mvt(PolyBenchGroup):
    NAME = 'mvt'


class Gemm(PolyBenchGroup):
    NAME = 'gemm'


class Gemver(PolyBenchGroup):
    NAME = 'gemver'


class Gesummv(PolyBenchGroup):
    NAME = 'gesummv'


class Symm(PolyBenchGroup):
    NAME = 'symm'


class Syr2k(PolyBenchGroup):
    NAME = 'syr2k'


class Syrk(PolyBenchGroup):
    NAME = 'syrk'


class Trmm(PolyBenchGroup):
    NAME = 'trmm'


class Cholesky(PolyBenchGroup):
    NAME = 'cholesky'


class Durbin(PolyBenchGroup):
    NAME = 'durbin'


class Gramschmidt(PolyBenchGroup):
    NAME = 'gramschmidt'


class Lu(PolyBenchGroup):
    NAME = 'lu'


class LuDCMP(PolyBenchGroup):
    NAME = 'ludcmp'


class Trisolv(PolyBenchGroup):
    NAME = 'trisolv'


class Deriche(PolyBenchGroup):
    NAME = 'deriche'


class FloydWarshall(PolyBenchGroup):
    NAME = 'floyd-warshall'


class Nussinov(PolyBenchGroup):
    NAME = 'nussinov'


class Adi(PolyBenchGroup):
    NAME = 'adi'


class FDTD2D(PolyBenchGroup):
    NAME = 'fdtd-2d'


class Jacobi1D(PolyBenchGroup):
    NAME = 'jacobi-1d'


class Jacobi2Dimper(PolyBenchGroup):
    NAME = 'jacobi-2d'


class Seidel2D(PolyBenchGroup):
    NAME = 'seidel-2d'


class Heat3D(PolyBenchGroup):
    NAME = 'heat-3d'
