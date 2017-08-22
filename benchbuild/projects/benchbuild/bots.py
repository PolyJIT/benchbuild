import os

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make, mkdir
from benchbuild.utils.compiler import lt_clang
from benchbuild.utils.downloader import Git
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap
from plumbum import local


class BOTSGroup(Project):
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
    VERSION = '1.1.2'

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
        "alignment": [
            "prot.100.aa",
            "prot.20.aa"
        ],
        "floorplan": [
            "input.15",
            "input.20",
            "input.5"
        ],
        "health": [
            "large.input",
            "medium.input",
            "small.input",
            "test.input"
        ],
        "knapsack": [
            "knapsack-012.input",
            "knapsack-016.input",
            "knapsack-020.input",
            "knapsack-024.input",
            "knapsack-032.input",
            "knapsack-036.input",
            "knapsack-040.input",
            "knapsack-044.input",
            "knapsack-048.input",
            "knapsack-064.input",
            "knapsack-096.input",
            "knapsack-128.input"
        ],
        "uts": [
            "huge.input",
            "large.input",
            "medium.input",
            "small.input",
            "test.input",
            "tiny.input"
        ]
    }

    def __init__(self, exp):
        super(BOTSGroup, self).__init__(exp, "bots")
        self.sourcedir = os.path.join(
            str(CFG["src_dir"]), "bots", self.path_dict[self.name],
            self.name)
        self.setup_derived_filenames()

    SRC_FILE = "bots.git"
    src_uri = "https://github.com/bsc-pm/bots"

    def download(self):
        Git(self.src_uri, self.SRC_FILE)

    def configure(self):
        makefile_config = os.path.join(self.SRC_FILE, "config", "make.config")
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)

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

    def build(self):
        mkdir(os.path.join(self.SRC_FILE, "bin"))
        with local.cwd(self.SRC_FILE):
            run(make["-C", self.path_dict[self.name]])

    def run_tests(self, experiment, run):
        binary_name = "{name}.benchbuild.serial".format(name=self.name)
        exp = wrap(os.path.join(self.SRC_FILE, "bin", binary_name), experiment)

        if self.name in self.input_dict:
            for test_input in self.input_dict[self.name]:
                input_file = os.path.join(self.SRC_FILE, "inputs", self.name, test_input)

                run(exp["-f", input_file])
        else:
            run(exp)


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


# FIXME: Seems to be broken - class UTS(BOTSGroup):
# FIXME: Seems to be broken -     NAME = 'uts'