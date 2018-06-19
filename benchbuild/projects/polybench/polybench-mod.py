from os import path

from benchbuild.projects.polybench.polybench import PolyBenchGroup
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import Git

class PolybenchModGroup(PolyBenchGroup):
    DOMAIN = 'polybench'
    GROUP  = 'polybench-mod'
    DOMAIN = 'polybench'
    VERSION = '4.2-1'

    src_dir = "polybench-c-{0}-mod".format(VERSION)
    SRC_FILE = 'polybench-c-{0}.git'.format(VERSION)
    SRC_URI = "https://github.com/simbuerg/{0}".format(SRC_FILE)

    def download(self):
        Git(self.SRC_URI, self.src_dir)

    def build(self):
        from benchbuild.utils.run import run
        src_file = path.join(self.name + ".dir", self.name + ".c")
        kernel_file = path.join("{name}.dir".format(name=self.name),
                                "{name}_kernel.c".format(name=self.name))
        cflags = self.cflags
        ldflags = self.ldflags
        self.cflags = []
        self.ldflags = []

        clang_no_opts = cc(self)

        self.cflags = cflags
        self.ldflags = ldflags

        polybench_opts = [
            "-DEXTRALARGE_DATASET",
            "-DPOLYBENCH_USE_C99_PROTO",
            "-DPOLYBENCH_DUMP_ARRAYS",
            "-DPOLYBENCH_USE_RESTRICT"
        ]
        run(clang_no_opts[
            "-I", "utilities", "-I", self.name, polybench_opts,
            "utilities/polybench.c", kernel_file, src_file,
            "-lm", "-o", self.run_f + ".no-opts"])
        clang = cc(self)
        run(clang[
            "-I", "utilities", "-I", self.name, polybench_opts,
            "utilities/polybench.c", kernel_file, src_file,
            "-lm", "-o", self.run_f])

class Correlation(PolybenchModGroup):
    NAME = 'correlation'


class Covariance(PolybenchModGroup):
    NAME = 'covariance'


class TwoMM(PolybenchModGroup):
    NAME = '2mm'


class ThreeMM(PolybenchModGroup):
    NAME = '3mm'


class Atax(PolybenchModGroup):
    NAME = 'atax'


class BicG(PolybenchModGroup):
    NAME = 'bicg'


class Doitgen(PolybenchModGroup):
    NAME = 'doitgen'


class Mvt(PolybenchModGroup):
    NAME = 'mvt'


class Gemm(PolybenchModGroup):
    NAME = 'gemm'


class Gemver(PolybenchModGroup):
    NAME = 'gemver'


class Gesummv(PolybenchModGroup):
    NAME = 'gesummv'


class Symm(PolybenchModGroup):
    NAME = 'symm'


class Syr2k(PolybenchModGroup):
    NAME = 'syr2k'


class Syrk(PolybenchModGroup):
    NAME = 'syrk'


class Trmm(PolybenchModGroup):
    NAME = 'trmm'


class Cholesky(PolybenchModGroup):
    NAME = 'cholesky'


class Durbin(PolybenchModGroup):
    NAME = 'durbin'


class Gramschmidt(PolybenchModGroup):
    NAME = 'gramschmidt'


class Lu(PolybenchModGroup):
    NAME = 'lu'


class LuDCMP(PolybenchModGroup):
    NAME = 'ludcmp'


class Trisolv(PolybenchModGroup):
    NAME = 'trisolv'


class Deriche(PolybenchModGroup):
    NAME = 'deriche'


class FloydWarshall(PolybenchModGroup):
    NAME = 'floyd-warshall'


class Nussinov(PolybenchModGroup):
    NAME = 'nussinov'


class Adi(PolybenchModGroup):
    NAME = 'adi'


class FDTD2D(PolybenchModGroup):
    NAME = 'fdtd-2d'


class Jacobi1D(PolybenchModGroup):
    NAME = 'jacobi-1d'


class Jacobi2Dimper(PolybenchModGroup):
    NAME = 'jacobi-2d'


class Seidel2D(PolybenchModGroup):
    NAME = 'seidel-2d'


class Heat3D(PolybenchModGroup):
    NAME = 'heat-3d'
