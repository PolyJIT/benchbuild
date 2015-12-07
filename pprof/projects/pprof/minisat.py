from pprof.projects.pprof.group import PprofGroup
from os import path, getenv
from glob import glob
from plumbum import local


class Minisat(PprofGroup):
    """ minisat benchmark """

    NAME = 'minisat'
    DOMAIN = 'verification'

    def run_tests(self, experiment):
        from pprof.project import wrap
        from pprof.utils.run import run

        minisat_dir = path.join(self.builddir, self.src_dir)

        exp = wrap(
            path.join(minisat_dir, "build", "dynamic", "bin", "minisat"),
            experiment)

        testfiles = glob(path.join(self.testdir, "*.cnf.gz"))
        minisat_dir = path.join(self.builddir, self.src_dir)
        minisat_lib_path = path.join(minisat_dir, "build", "dynamic", "lib")

        for test_f in testfiles:
            with local.env(LD_LIBRARY_PATH=minisat_lib_path + ":" + getenv(
                    "LD_LIBRARY_PATH", "")):
                run((exp < test_f), None)

    src_dir = "minisat.git"
    src_uri = "https://github.com/niklasso/minisat"

    def download(self):
        from pprof.utils.downloader import Git
        from plumbum.cmd import git

        minisat_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            Git(self.src_uri, self.src_dir)
            with local.cwd(minisat_dir):
                git("fetch", "origin", "pull/17/head:clang")
                git("checkout", "clang")

    def configure(self):
        from plumbum.cmd import make
        from pprof.utils.run import run

        minisat_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(minisat_dir):
            run(make["config"])

    def build(self):
        from plumbum.cmd import make
        from pprof.utils.compiler import lt_clang, lt_clang_cxx
        from pprof.utils.run import run

        minisat_dir = path.join(self.builddir, self.src_dir)
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        with local.cwd(minisat_dir):
            run(make["CC=" + str(clang), "CXX=" + str(clang_cxx), "clean",
                     "lsh", "sh"])
