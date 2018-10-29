from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make, mkdir


@download.with_git("https://github.com/bsc-pm/bots", limit=5)
class BOTSGroup(project.Project):
    """
    Barcelona OpenMP Task Suite.

    Barcelona OpenMP Task Suite is a collection of applications that allow
    to test OpenMP tasking implementations and compare its behaviour under
    certain circumstances: task tiedness, throttle and cut-offs mechanisms,
    single/multiple task generators, etc.

    Alignment: Aligns sequences of proteins.
    FFT: Computes a Fast Fourier Transformation.
    Floorplan: Computes the optimal placement of cells in a floorplan.
    Health: Simulates a country health system.
    NQueens: Finds solutions of the N Queens problem.
    Sort: Uses a mixture of sorting algorithms to sort a vector.
    SparseLU: Computes the LU factorization of a sparse matrix.
    Strassen: Computes a matrix multiply with Strassen's method.
    """

    DOMAIN = 'bots'
    GROUP = 'bots'
    VERSION = 'HEAD'

    path_dict = {
        "alignment": "serial/alignment",
        "fft": "serial/fft",
        "fib": "serial/fib",
        "floorplan": "serial/floorplan",
        "health": "serial/health",
        "knapsack": "serial/knapsack",
        "nqueens": "serial/nqueens",
        "sort": "serial/sort",
        "sparselu": "serial/sparselu",
        "strassen": "serial/strassen",
        "uts": "serial/uts"
    }

    input_dict = {
        "alignment": ["prot.100.aa", "prot.20.aa"],
        "floorplan": ["input.15", "input.20", "input.5"],
        "health": ["large.input", "medium.input", "small.input", "test.input"],
        "knapsack": [
            "knapsack-012.input", "knapsack-016.input", "knapsack-020.input",
            "knapsack-024.input", "knapsack-032.input", "knapsack-036.input",
            "knapsack-040.input", "knapsack-044.input", "knapsack-048.input",
            "knapsack-064.input", "knapsack-096.input", "knapsack-128.input"
        ],
        "uts": [
            "huge.input", "large.input", "medium.input", "small.input",
            "test.input", "tiny.input"
        ]
    }

    SRC_FILE = "bots.git"

    def compile(self):
        self.download()
        makefile_config = local.path(self.src_file) / "config" / "make.config"
        clang = compiler.cc(self)

        with open(makefile_config, 'w') as config:
            lines = [
                "LABEL=benchbuild",
                "ENABLE_OMPSS=",
                "OMPSSC=",
                "OMPC=",
                "CC={cc}",
                "OMPSSLINK=",
                "OMPLINK={cc} -fopenmp",
                "CLINK={cc}",
                "OPT_FLAGS=",
                "CC_FLAGS=",
                "OMPC_FLAGS=",
                "OMPSSC_FLAGS=",
                "OMPC_FINAL_FLAGS=",
                "OMPSSC_FINAL_FLAG=",
                "CLINK_FLAGS=",
                "OMPLINK_FLAGS=",
                "OMPSSLINK_FLAGS=",
            ]
            lines = [l.format(cc=clang) + "\n" for l in lines]
            config.writelines(lines)
        mkdir(local.path(self.src_file) / "bin")
        with local.cwd(self.src_file):
            run.run(make["-C", self.path_dict[self.name]])

    def run_tests(self, runner):
        binary_name = "{name}.benchbuild.serial".format(name=self.name)
        binary_path = local.path(self.src_file) / "bin" / binary_name
        exp = wrapping.wrap(binary_path, self)

        if self.name in self.input_dict:
            for test_input in self.input_dict[self.name]:
                input_file = local.path(
                    self.src_file) / "inputs" / self.name / test_input
                runner(exp["-f", input_file])
        else:
            runner(exp)


class Alignment(BOTSGroup):
    NAME = 'alignment'


class FFT(BOTSGroup):
    NAME = 'fft'


class Fib(BOTSGroup):
    NAME = 'fib'


class FloorPlan(BOTSGroup):
    NAME = 'floorplan'


class Health(BOTSGroup):
    NAME = 'health'


class Knapsack(BOTSGroup):
    NAME = 'knapsack'


class NQueens(BOTSGroup):
    NAME = 'nqueens'


class Sort(BOTSGroup):
    NAME = 'sort'


class SparseLU(BOTSGroup):
    NAME = 'sparselu'


class Strassen(BOTSGroup):
    NAME = 'strassen'


class UTS(BOTSGroup):
    NAME = 'uts'
