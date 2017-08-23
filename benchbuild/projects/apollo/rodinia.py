import os

from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Wget
from benchbuild.project import Project
from benchbuild.utils.cmd import sh, tar
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap
from plumbum import local


class RodiniaGroup(Project):
    DOMAIN = 'rodinia'
    GROUP = 'rodinia'
    VERSION = '3.1'

    config = {}

    def __init__(self, exp):
        super(RodiniaGroup, self).__init__(exp, "rodinia")
        self.in_src_dir = os.path.join(
            self.src_dir, self.config["dir"]
        )
        self.setup_derived_filenames()

    src_dir = "rodinia_{0}".format(VERSION)
    SRC_FILE = "{0}.tar.bz2".format(src_dir)
    src_uri = ("http://www.cs.virginia.edu/~kw5na/lava/Rodinia/Packages/"
               "Current/{0}".format(SRC_FILE))

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xf", os.path.join('.', self.SRC_FILE))

    def configure(self):
        pass

    def select_compiler(self, cc, cxx):
        return cc

    def build(self):
        c_compiler = lt_clang(self.cflags,
                              self.ldflags,
                              self.compiler_extension)
        cxx_compiler = lt_clang_cxx(self.cflags,
                                    self.ldflags,
                                    self.compiler_extension)

        with local.cwd(self.in_src_dir):
            for outfile, srcfiles in self.config['src'].items():
                compiler = self.select_compiler(c_compiler, cxx_compiler)
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

    config = {
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

    config = {
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

    def select_compiler(self, _, cxx):
        return cxx


class BPlusTree(RodiniaGroup):
    NAME = 'b+tree'

    config = {
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

    config = {
        "dir": "openmp/cfd",
        "src": {
            "euler3d_cpu": [
                "euler3d_cpu.cpp"
            ]
        }
    }

    def select_compiler(self, _, cxx):
        return cxx


class HeartWall(RodiniaGroup):
    NAME = 'heartwall'

    config = {
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

    config = {
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

    def select_compiler(self, _, cxx):
        return cxx


class Hotspot3D(RodiniaGroup):
    NAME = 'hotspot3D'

    config = {
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

    config = {
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

    config = {
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

    config = {
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

    config = {
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

#TODO: class MummerGPU(RodiniaGroup):
#TODO:     NAME = 'mummergpu'
#TODO:

#FIXME: Compiles, but SIGABRT class Myocyte(RodiniaGroup):
#FIXME: Compiles, but SIGABRT     NAME = 'myocyte'
#FIXME: Compiles, but SIGABRT
#FIXME: Compiles, but SIGABRT     config = {
#FIXME: Compiles, but SIGABRT         "dir": "openmp/myocyte",
#FIXME: Compiles, but SIGABRT         "src": {
#FIXME: Compiles, but SIGABRT             "./myocyte.out": [
#FIXME: Compiles, but SIGABRT                 "main.c"
#FIXME: Compiles, but SIGABRT             ]
#FIXME: Compiles, but SIGABRT         },
#FIXME: Compiles, but SIGABRT         "flags": [
#FIXME: Compiles, but SIGABRT             "-lm",
#FIXME: Compiles, but SIGABRT             "-fopenmp"
#FIXME: Compiles, but SIGABRT         ]
#FIXME: Compiles, but SIGABRT     }

class NN(RodiniaGroup):
    NAME = 'nn'

    config = {
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

    config = {
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

    def select_compiler(self, _, cxx):
        return cxx


class ParticleFilter(RodiniaGroup):
    NAME = 'particlefilter'

    config = {
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

    config = {
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

    def select_compiler(self, _, cxx):
        return cxx

class SRAD1(RodiniaGroup):
    NAME = 'srad-1'

    config = {
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

    config = {
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

    def select_compiler(self, _, cxx):
        return cxx

class StreamCluster(RodiniaGroup):
    NAME = 'streamcluster'

    config = {
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

    def select_compiler(self, _, cxx):
        return cxx
