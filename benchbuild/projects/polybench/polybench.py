import logging

from benchbuild.environments import container
from benchbuild.project import Project
from benchbuild.source import HTTP
from benchbuild.settings import CFG
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
    DOMAIN: str = 'polybench'
    GROUP: str = 'polybench'
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
        HTTP(remote={
            '4.2':
            'http://downloads.sourceforge.net/project/polybench/polybench-c-4.2.tar.gz'
        },
             local='polybench.tar.gz')
    ]

    def compile_verify(self, compiler_args, polybench_opts):
        polybench_opts.append("-DPOLYBENCH_DUMP_ARRAYS")

        cflags = self.cflags
        ldflags = self.ldflags

        self.cflags = []
        self.ldflags = []

        clang_no_opts = compiler.cc(self)
        clang_no_opts = run.watch(clang_no_opts)

        self.cflags = cflags
        self.ldflags = ldflags
        clang_no_opts(polybench_opts, compiler_args, "-o",
                      self.name + ".no-opts", "-lm")
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
        clang = compiler.cc(self)
        clang = run.watch(clang)
        clang("-I", utils_dir, "-I", src_sub, polybench_opts,
              utils_dir / "polybench.c", src_file, "-lm", "-o", self.name)

    def run_tests(self):
        def filter_stderr(stderr_raw, stderr_filtered):
            """Extract dump_arrays_output from stderr."""
            with open(stderr_raw, 'r') as stderr:
                with open(stderr_filtered, 'w') as stderr_filt:
                    stderr_filt.writelines(
                        get_dump_arrays_output(stderr.readlines()))

        polybench_opts = CFG["projects"]["polybench"]
        verify = bool(polybench_opts["verify"])

        binary = local.path(self.name)
        opt_stderr_raw = binary + ".stderr"
        opt_stderr_filtered = opt_stderr_raw + ".filtered"

        polybench_bin = wrapping.wrap(binary, self)
        polybench_bin = run.watch(polybench_bin)
        polybench_bin()

        filter_stderr(opt_stderr_raw, opt_stderr_filtered)

        if verify:
            binary = local.path(self.name + ".no-opts")
            noopt_stderr_raw = binary + ".stderr"
            noopt_stderr_filtered = noopt_stderr_raw + ".filtered"

            with local.env(BB_IS_BASELINE=True):
                polybench_bin = wrapping.wrap(binary, self)
                polybench_bin = run.watch(polybench_bin)
                polybench_bin()
            filter_stderr(noopt_stderr_raw, noopt_stderr_filtered)

            diff_ = diff[noopt_stderr_filtered, opt_stderr_filtered]
            diff_ = run.watch(diff_)
            diff_(retcode=0)


class Correlation(PolyBenchGroup):
    NAME: str = 'correlation'


class Covariance(PolyBenchGroup):
    NAME: str = 'covariance'


class TwoMM(PolyBenchGroup):
    NAME: str = '2mm'


class ThreeMM(PolyBenchGroup):
    NAME: str = '3mm'


class Atax(PolyBenchGroup):
    NAME: str = 'atax'


class BicG(PolyBenchGroup):
    NAME: str = 'bicg'


class Doitgen(PolyBenchGroup):
    NAME: str = 'doitgen'


class Mvt(PolyBenchGroup):
    NAME: str = 'mvt'


class Gemm(PolyBenchGroup):
    NAME: str = 'gemm'


class Gemver(PolyBenchGroup):
    NAME: str = 'gemver'


class Gesummv(PolyBenchGroup):
    NAME: str = 'gesummv'


class Symm(PolyBenchGroup):
    NAME: str = 'symm'


class Syr2k(PolyBenchGroup):
    NAME: str = 'syr2k'


class Syrk(PolyBenchGroup):
    NAME: str = 'syrk'


class Trmm(PolyBenchGroup):
    NAME: str = 'trmm'


class Cholesky(PolyBenchGroup):
    NAME: str = 'cholesky'


class Durbin(PolyBenchGroup):
    NAME: str = 'durbin'


class Gramschmidt(PolyBenchGroup):
    NAME: str = 'gramschmidt'


class Lu(PolyBenchGroup):
    NAME: str = 'lu'


class LuDCMP(PolyBenchGroup):
    NAME: str = 'ludcmp'


class Trisolv(PolyBenchGroup):
    NAME: str = 'trisolv'


class Deriche(PolyBenchGroup):
    NAME: str = 'deriche'


class FloydWarshall(PolyBenchGroup):
    NAME: str = 'floyd-warshall'


class Nussinov(PolyBenchGroup):
    NAME: str = 'nussinov'


class Adi(PolyBenchGroup):
    NAME: str = 'adi'


class FDTD2D(PolyBenchGroup):
    NAME: str = 'fdtd-2d'


class Jacobi1D(PolyBenchGroup):
    NAME: str = 'jacobi-1d'


class Jacobi2Dimper(PolyBenchGroup):
    NAME: str = 'jacobi-2d'


class Seidel2D(PolyBenchGroup):
    NAME: str = 'seidel-2d'


class Heat3D(PolyBenchGroup):
    NAME: str = 'heat-3d'
