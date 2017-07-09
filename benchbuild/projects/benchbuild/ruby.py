from os import path
from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.settings import CFG
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.cmd import ruby, make, tar
from plumbum import local


class Ruby(BenchBuildGroup):
    NAME = 'ruby'
    DOMAIN = 'compilation'
    VERSION = '2.2.2'

    src_dir = "ruby-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.gz"
    src_uri = "http://cache.ruby-lang.org/pub/ruby/{0}/".format(VERSION) \
        + SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xfz", self.SRC_FILE)

    def configure(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)
        with local.cwd(self.src_dir):
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure = local["./configure"]
                run(configure["--with-static-linked-ext", "--disable-shared"])

    def build(self):
        with local.cwd(self.src_dir):
            run(make["-j", CFG["jobs"]])

    def run_tests(self, experiment, run):
        exp = wrap(path.join(self.src_dir, "ruby"), experiment)

        with local.env(RUBYOPT=""):
            run(ruby[path.join(self.testdir, "benchmark", "run.rb"),
                     "--ruby=\"" + str(exp) + "\"", "--opts=\"-I" + path.join(
                         self.testdir, "lib") + " -I" + path.join(
                             self.testdir, ".") + " -I" + path.join(
                                 self.testdir, ".ext", "common") + "\"", "-r"])
