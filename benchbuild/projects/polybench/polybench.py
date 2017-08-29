import logging
from os import path

import benchbuild.extensions as ext
from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.compiler import lt_clang
from benchbuild.utils.downloader import Wget
from benchbuild.utils.wrapping import wrap
from benchbuild.utils.cmd import tar, cp, diff

from plumbum import local


LOG = logging.getLogger(__name__)


def get_dump_arrays_output(data):
    start_tag = "==BEGIN"
    end_tag = "==END"

    found_start = False
    found_end = False

    out = []
    for line in data:
        if start_tag in line:
            found_start = True
        if end_tag in line:
            found_end = True
        if found_start and not found_end:
            out.append(line)

    return out


class PolyBenchGroup(Project):
    DOMAIN = 'polybench'
    GROUP = 'polybench'
    VERSION = '4.2'
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
        self.sourcedir = path.join(
            str(CFG["src_dir"]), "polybench", self.path_dict[self.name],
            self.name)
        self.setup_derived_filenames()

    src_dir = "polybench-c-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.gz"
    src_uri = "http://downloads.sourceforge.net/project/polybench/" + SRC_FILE

    def download(self):
        Wget(self.src_uri, self.src_file)
        tar('xfz', path.join(self.builddir, self.src_file))

    def configure(self):
        cp("-ar", path.join(self.src_dir, self.path_dict[self.name],
                            self.name), self.name + ".dir")
        cp("-ar", path.join(self.src_dir, "utilities"), ".")

    def build(self):
        from benchbuild.utils.run import run
        src_file = path.join(self.name + ".dir", self.name + ".c")
        clang_no_opts = lt_clang([], [], self.compiler_extension)
        polybench_opts = [
            "-DPOLYBENCH_USE_C99_PROTO",
            "-DLARGE_DATASET",
            "-DPOLYBENCH_DUMP_ARRAYS",
            "-DPOLYBENCH_USE_RESTRICT"
        ]
        run(clang_no_opts[
            "-I", "utilities", "-I", self.name,
            polybench_opts,
            "utilities/polybench.c", src_file, "-lm", "-o",
            self.run_f + ".no-opts"])
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        run(clang["-I", "utilities", "-I", self.name,
                  polybench_opts,
                  "utilities/polybench.c", src_file, "-lm", "-o", self.run_f])

    def run_tests(self, experiment, run):
        noopts_file = self.run_f + ".no-opts"
        noopts_file_stderr = noopts_file + ".stderr"
        noopts_file_stderr_2 = noopts_file_stderr + ".2"

        opts_file = self.run_f
        opts_file_stderr = self.run_f + ".stderr"
        opts_file_stderr_2 = opts_file_stderr + ".2"

        run(wrap(opts_file, experiment))
        with local.env(BB_IS_BASELINE=True):
            run(wrap(noopts_file, experiment))

        with open(noopts_file_stderr, 'r') as inf:
            stderr = inf.readlines()
            with open(noopts_file_stderr_2, 'w') as fd_stderr:
                fd_stderr.writelines(get_dump_arrays_output(stderr))

        with open(opts_file_stderr, 'r') as inf:
            stderr = inf.readlines()
            with open(opts_file_stderr_2, 'w') as fd_stderr:
                fd_stderr.writelines(get_dump_arrays_output(stderr))

        diff_cmd = diff[noopts_file_stderr_2, opts_file_stderr_2]
        run(diff_cmd, retcode=0)


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
