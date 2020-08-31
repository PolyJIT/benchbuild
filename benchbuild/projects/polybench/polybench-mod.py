from plumbum import local

import benchbuild as bb
from benchbuild.projects.polybench.polybench import PolyBenchGroup
from benchbuild.settings import CFG
from benchbuild.source import Git


class PolybenchModGroup(PolyBenchGroup):
    DOMAIN = 'polybench'
    GROUP = 'polybench-mod'
    DOMAIN = 'polybench'
    SOURCE = [
        Git(remote='https://github.com/simbuerg/polybench-c-4.2-1.git',
            local='polybench.git',
            limit=5,
            refspec='HEAD')
    ]

    def compile(self):
        polybench_repo = local.path(self.source_of('polybench.git'))

        polybench_opts = CFG["projects"]["polybench"]
        verify = bool(polybench_opts["verify"])
        workload = str(polybench_opts["workload"])

        src_dir = polybench_repo
        src_sub = src_dir / self.path_dict[self.name] / self.name

        src_file = src_sub / (self.name + ".c")
        kernel_file = src_sub / (self.name + "_kernel.c")
        utils_dir = src_dir / "utilities"

        polybench_opts = [
            "-D" + str(workload), "-DPOLYBENCH_USE_C99_PROTO",
            "-DPOLYBENCH_USE_RESTRICT"
        ]

        if verify:
            polybench_opts = self.compile_verify([
                "-I", utils_dir, "-I", src_sub, utils_dir / "polybench.c",
                kernel_file, src_file, "-lm"
            ], polybench_opts)

        clang = bb.compiler.cc(self)
        _clang = bb.watch(clang)
        _clang("-I", utils_dir, "-I", src_sub, polybench_opts,
               utils_dir / "polybench.c", kernel_file, src_file, "-lm", "-o",
               self.name)


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
