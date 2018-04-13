#pylint: disable=E1135,E1136
import os
import attr

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import sh, tar
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@attr.s
class RodiniaGroup(Project):
    """Generic handling of Rodinia benchmarks."""
    DOMAIN = 'rodinia'
    GROUP = 'rodinia'
    VERSION = '3.1'
    SRC_FILE = "rodinia_{0}.tar.bz2".format(VERSION)
    CONFIG = {}

    src_dir = attr.ib(default="rodinia_{0}".format(VERSION))

    src_uri = attr.ib(
        default="http://www.cs.virginia.edu/~kw5na/lava/Rodinia/Packages/"
                "Current/{0}".format(SRC_FILE))

    config = attr.ib(default=attr.Factory(
        lambda self: type(self).CONFIG, takes_self=True))

    in_src_dir = attr.ib(default=attr.Factory(
        lambda self: os.path.join(self.src_dir, self.config["dir"]),
        takes_self=True))

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xf", os.path.join('.', self.SRC_FILE))

    def configure(self):
        pass

    @staticmethod
    def select_compiler(c_compiler, _):
        return c_compiler

    def build(self):
        c_compiler = lt_clang(self.cflags,
                              self.ldflags,
                              self.compiler_extension)
        cxx_compiler = lt_clang_cxx(self.cflags,
                                    self.ldflags,
                                    self.compiler_extension)

        with local.cwd(self.in_src_dir):
            for outfile, srcfiles in self.config['src'].items():
                cls = type(self)
                compiler = cls.select_compiler(c_compiler, cxx_compiler)
                if "flags" in self.config:
                    compiler = compiler[self.config["flags"]]
                compiler = compiler[srcfiles]
                compiler = compiler["-o", outfile]
                run(compiler)

    def run_tests(self, experiment, runner):
        for outfile in self.config['src']:
            wrap(os.path.join(self.in_src_dir, outfile), experiment)

        with local.cwd(self.in_src_dir):
            test_runner = sh["./run"]
            runner(test_runner)


class Backprop(RodiniaGroup):
    NAME = 'backprop'
    CONFIG = {
        "dir": "openmp/backprop",
        "src": {
            NAME: [
                "backprop_kernel.c",
                "imagenet.c",
                "facetrain.c",
                "backprop.c"
            ]
        },
        "flags": [
            "-fopenmp",
            "-lm"
        ]
    }


class BFS(RodiniaGroup):
    NAME = 'bfs'
    CONFIG = {
        "dir": "openmp/bfs",
        "src": {
            NAME: [
                "bfs.cpp"
            ]
        },
        "flags": [
            "-fopenmp",
            "-UOPEN"
        ]
    }

    @staticmethod
    def select_compiler(_, compiler):
        return compiler


class BPlusTree(RodiniaGroup):
    NAME = 'b+tree'
    CONFIG = {
        "dir": "openmp/b+tree",
        "src": {
            "b+tree.out": [
                "./main.c",
                "./kernel/kernel_cpu.c",
                "./kernel/kernel_cpu_2.c",
                "./util/timer/timer.c",
                "./util/num/num.c"
            ]
        },
        "flags": [
            "-fopenmp",
            "-lm"
        ]
    }


class CFD(RodiniaGroup):
    NAME = 'cfd'
    CONFIG = {
        "dir": "openmp/cfd",
        "src": {
            "euler3d_cpu": [
                "euler3d_cpu.cpp"
            ]
        }
    }

    @staticmethod
    def select_compiler(_, compiler):
        return compiler


class HeartWall(RodiniaGroup):
    NAME = 'heartwall'
    CONFIG = {
        "dir": "openmp/heartwall",
        "src": {
            NAME: [
                "./AVI/avimod.c",
                "./AVI/avilib.c",
                "./main.c"
            ]
        },
        "flags": [
            "-I./AVI",
            "-fopenmp",
            "-lm"
        ]
    }


class Hotspot(RodiniaGroup):
    NAME = 'hotspot'
    CONFIG = {
        "dir": "openmp/hotspot",
        "src": {
            NAME: [
                "hotspot_openmp.cpp"
            ]
        },
        "flags": [
            "-fopenmp"
        ]
    }

    @staticmethod
    def select_compiler(_, compiler):
        return compiler


class Hotspot3D(RodiniaGroup):
    NAME = 'hotspot3D'
    CONFIG = {
        "dir": "openmp/hotspot3D",
        "src": {
            "3D": [
                "./3D.c"
            ]
        },
        "flags": [
            "-fopenmp",
            "-lm"
        ]
    }


class KMeans(RodiniaGroup):
    NAME = 'kmeans'
    CONFIG = {
        "dir": "openmp/kmeans",
        "src": {
            "./kmeans_serial/kmeans": [
                "./kmeans_serial/kmeans_clustering.c",
                "./kmeans_serial/kmeans.c",
                "./kmeans_serial/getopt.c",
                "./kmeans_serial/cluster.c"
            ],
            "./kmeans_openmp/kmeans": [
                "./kmeans_openmp/kmeans_clustering.c",
                "./kmeans_openmp/kmeans.c",
                "./kmeans_openmp/getopt.c",
                "./kmeans_openmp/cluster.c"
            ]
        },
        "flags": [
            "-lm",
            "-fopenmp"
        ]
    }


class LavaMD(RodiniaGroup):
    NAME = 'lavaMD'
    CONFIG = {
        "dir": "openmp/lavaMD",
        "src": {
            NAME: [
                "./main.c",
                "./util/timer/timer.c",
                "./util/num/num.c",
                "./kernel/kernel_cpu.c"
            ]
        },
        "flags": [
            "-lm",
            "-fopenmp"
        ]
    }


class Leukocyte(RodiniaGroup):
    NAME = 'leukocyte'
    CONFIG = {
        "dir": "openmp/leukocyte",
        "src": {
            NAME: [
                "./meschach_lib/memstat.c",
                "./meschach_lib/meminfo.c",
                "./meschach_lib/version.c",
                "./meschach_lib/ivecop.c",
                "./meschach_lib/matlab.c",
                "./meschach_lib/machine.c",
                "./meschach_lib/otherio.c",
                "./meschach_lib/init.c",
                "./meschach_lib/submat.c",
                "./meschach_lib/pxop.c",
                "./meschach_lib/matop.c",
                "./meschach_lib/vecop.c",
                "./meschach_lib/memory.c",
                "./meschach_lib/matrixio.c",
                "./meschach_lib/err.c",
                "./meschach_lib/copy.c",
                "./meschach_lib/bdfactor.c",
                "./meschach_lib/mfunc.c",
                "./meschach_lib/fft.c",
                "./meschach_lib/svd.c",
                "./meschach_lib/schur.c",
                "./meschach_lib/symmeig.c",
                "./meschach_lib/hessen.c",
                "./meschach_lib/norm.c",
                "./meschach_lib/update.c",
                "./meschach_lib/givens.c",
                "./meschach_lib/hsehldr.c",
                "./meschach_lib/solve.c",
                "./meschach_lib/qrfactor.c",
                "./meschach_lib/chfactor.c",
                "./meschach_lib/bkpfacto.c",
                "./meschach_lib/lufactor.c",
                "./meschach_lib/iternsym.c",
                "./meschach_lib/itersym.c",
                "./meschach_lib/iter0.c",
                "./meschach_lib/spswap.c",
                "./meschach_lib/spbkp.c",
                "./meschach_lib/splufctr.c",
                "./meschach_lib/spchfctr.c",
                "./meschach_lib/sparseio.c",
                "./meschach_lib/sprow.c",
                "./meschach_lib/sparse.c",
                "./meschach_lib/zfunc.c",
                "./meschach_lib/znorm.c",
                "./meschach_lib/zmatop.c",
                "./meschach_lib/zvecop.c",
                "./meschach_lib/zmemory.c",
                "./meschach_lib/zmatio.c",
                "./meschach_lib/zcopy.c",
                "./meschach_lib/zmachine.c",
                "./meschach_lib/zschur.c",
                "./meschach_lib/zhessen.c",
                "./meschach_lib/zgivens.c",
                "./meschach_lib/zqrfctr.c",
                "./meschach_lib/zhsehldr.c",
                "./meschach_lib/zmatlab.c",
                "./meschach_lib/zsolve.c",
                "./meschach_lib/zlufctr.c",
                "./OpenMP/detect_main.c",
                "./OpenMP/misc_math.c",
                "./OpenMP/track_ellipse.c",
                "./OpenMP/find_ellipse.c",
                "./OpenMP/avilib.c"
            ]
        },
        "flags": [
            "-DSPARSE",
            "-DCOMPLEX",
            "-DREAL_FLT",
            "-DREAL_DBL",
            "-I./meschach_lib",
            "-lm",
            "-lpthread",
            "-fopenmp"
        ]
    }

class LUD(RodiniaGroup):
    NAME = 'lud'
    CONFIG = {
        "dir": "openmp/lud",
        "src": {
            "./omp/lud_omp": [
                "./common/common.c",
                "./omp/lud_omp.c",
                "./omp/lud.c"
            ]
        },
        "flags": [
            "-I./common",
            "-lm",
            "-fopenmp"
        ]
    }

class Myocyte(RodiniaGroup):
    NAME = 'myocyte'
    CONFIG = {
        "dir": "openmp/myocyte",
        "src": {
            "./myocyte.out": [
                "main.c"
            ]
        },
        "flags": [
            "-lm",
            "-fopenmp"
        ]
    }

class NN(RodiniaGroup):
    NAME = 'nn'
    CONFIG = {
        "dir": "openmp/nn",
        "src": {
            NAME: [
                "./nn_openmp.c"
            ]
        },
        "flags": [
            "-lm",
            "-fopenmp"
        ]
    }

class NW(RodiniaGroup):
    NAME = 'nw'
    CONFIG = {
        "dir": "openmp/nw",
        "src": {
            "needle": [
                "./needle.cpp"
            ]
        },
        "flags": [
            "-lm",
            "-fopenmp"
        ]
    }

    @staticmethod
    def select_compiler(_, compiler):
        return compiler


class ParticleFilter(RodiniaGroup):
    NAME = 'particlefilter'
    CONFIG = {
        "dir": "openmp/particlefilter",
        "src": {
            "particle_filter": [
                "./ex_particle_OPENMP_seq.c"
            ]
        },
        "flags": [
            "-lm",
            "-fopenmp"
        ]
    }

class PathFinder(RodiniaGroup):
    NAME = 'pathfinder'
    CONFIG = {
        "dir": "openmp/pathfinder",
        "src": {
            "pathfinder": [
                "./pathfinder.cpp"
            ]
        },
        "flags": [
            "-fopenmp"
        ]
    }

    @staticmethod
    def select_compiler(_, compiler):
        return compiler

class SRAD1(RodiniaGroup):
    NAME = 'srad-1'
    CONFIG = {
        "dir": "openmp/srad/srad_v1",
        "src": {
            "srad": [
                "./main.c"
            ]
        },
        "flags": [
            "-I.",
            "-lm",
            "-fopenmp"
        ]
    }

class SRAD2(RodiniaGroup):
    NAME = 'srad-2'
    CONFIG = {
        "dir": "openmp/srad/srad_v2",
        "src": {
            "srad": [
                "./srad.cpp"
            ]
        },
        "flags": [
            "-lm",
            "-fopenmp"
        ]
    }

    @staticmethod
    def select_compiler(_, compiler):
        return compiler

class StreamCluster(RodiniaGroup):
    NAME = 'streamcluster'
    CONFIG = {
        "dir": "openmp/streamcluster",
        "src": {
            "./sc_omp": [
                "./streamcluster_omp.cpp"
            ]
        },
        "flags": [
            "-lpthread",
            "-fopenmp"
        ]
    }

    @staticmethod
    def select_compiler(_, compiler):
        return compiler
