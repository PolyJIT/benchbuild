from benchbuild.project import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run

from plumbum import local
from benchbuild.utils.cmd import make, tar

from os import path


class Python(BenchBuildGroup):
    """ python benchmarks """

    NAME = 'python'
    DOMAIN = 'compilation'

    src_dir = "Python-3.4.3"
    src_file = src_dir + ".tar.xz"
    src_uri = "https://www.python.org/ftp/python/3.4.3/" + src_file

    def download(self):
        Wget(self.src_uri, self.src_file)
        tar("xfJ", self.src_file)

    def configure(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        with local.cwd(self.src_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run(configure["--disable-shared", "--without-gcc"])

    def build(self):
        with local.cwd(self.src_dir):
            run(make)

    def run_tests(self, experiment):
        exp = wrap(path.join(self.src_dir, "python"), experiment)

        with local.cwd(self.src_dir):
            run(make["TESTPYTHON=" + str(exp), "-i", "test"])
