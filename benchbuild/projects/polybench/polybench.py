import logging
import typing as tp

from plumbum import local

import benchbuild as bb
from benchbuild.settings import CFG
from benchbuild.source import HTTP
from benchbuild.utils.cmd import diff, tar

LOG = logging.getLogger(__name__)
CFG['projects'] = {
    "polybench": {
        "verify": {
            "default": True,
            "desc": "Verify results with POLYBENCH_DUMP_ARRAYS."
        },
        "workload": {
            "default": "EXTRALARGE_DATASET",
            "desc": "Control the dataset variable for polybench."
        }
    }
}


def get_dump_arrays_output(data: tp.List[str]) -> tp.List[str]:
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


class PolyBenchGroup(bb.Project):
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

    SOURCE = [
        HTTP(
            remote={
                '4.2': (
                    'http://downloads.sourceforge.net/project/'
                    'polybench/polybench-c-4.2.tar.gz'
                )
            },
            local='polybench.tar.gz'
        )
    ]

    def compile_verify(self, compiler_args, polybench_opts):
        polybench_opts.append("-DPOLYBENCH_DUMP_ARRAYS")

        cflags = self.cflags
        ldflags = self.ldflags

        self.cflags = []
        self.ldflags = []

        clang_no_opts = bb.compiler.cc(self)
        _clang_no_opts = bb.watch(clang_no_opts)

        self.cflags = cflags
        self.ldflags = ldflags
        _clang_no_opts(
            polybench_opts, compiler_args, "-o", self.name + ".no-opts", "-lm"
        )
        return polybench_opts

    def compile(self):
        polybench_source = local.path(self.source_of('polybench.tar.gz'))
        polybench_version = self.version_of('polybench.tar.gz')

        polybench_opts = CFG["projects"]["polybench"]
        verify = bool(polybench_opts["verify"])
        workload = str(polybench_opts["workload"])

        tar('xfz', polybench_source)

        src_dir = local.path(f'./polybench-c-{polybench_version}')
        src_sub = src_dir / self.path_dict[self.name] / self.name

        src_file = src_sub / (self.name + ".c")
        utils_dir = src_dir / "utilities"

        polybench_opts = [
            "-DPOLYBENCH_USE_C99_PROTO", "-D" + str(workload),
            "-DPOLYBENCH_USE_RESTRICT"
        ]

        if verify:
            polybench_opts = self.compile_verify([
                "-I", utils_dir, "-I", src_sub, utils_dir / "polybench.c",
                src_file, "-lm"
            ], polybench_opts)
        clang = bb.compiler.cc(self)
        _clang = bb.watch(clang)
        _clang(
            "-I", utils_dir, "-I", src_sub, polybench_opts,
            utils_dir / "polybench.c", src_file, "-lm", "-o", self.name
        )

    def run_tests(self):

        def filter_stderr(stderr_raw, stderr_filtered):
            """Extract dump_arrays_output from stderr."""
            with open(stderr_raw, 'r') as stderr:
                with open(stderr_filtered, 'w') as stderr_filt:
                    stderr_filt.writelines(
                        get_dump_arrays_output(stderr.readlines())
                    )

        polybench_opts = CFG["projects"]["polybench"]
        verify = bool(polybench_opts["verify"])

        binary = local.cwd / self.name
        opt_stderr_raw = binary + ".stderr"
        opt_stderr_filtered = opt_stderr_raw + ".filtered"

        polybench_bin = bb.wrap(binary, self)
        _polybench_bin = bb.watch(polybench_bin)
        _polybench_bin()

        filter_stderr(opt_stderr_raw, opt_stderr_filtered)

        if verify:
            binary = local.cwd / (self.name + ".no-opts")
            noopt_stderr_raw = binary + ".stderr"
            noopt_stderr_filtered = noopt_stderr_raw + ".filtered"

            with local.env(BB_IS_BASELINE=True):
                polybench_bin = bb.wrap(binary, self)
                _polybench_bin = bb.watch(polybench_bin)
                _polybench_bin()
            filter_stderr(noopt_stderr_raw, noopt_stderr_filtered)

            _diff = bb.watch(diff[noopt_stderr_filtered, opt_stderr_filtered])
            _diff(retcode=0)


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
