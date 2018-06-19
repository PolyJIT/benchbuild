from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make, ruby, tar
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class Ruby(Project):
    NAME = 'ruby'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    VERSION = '2.2.2'

    src_dir = "ruby-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.gz"
    src_uri = "http://cache.ruby-lang.org/pub/ruby/{0}/".format(VERSION) \
        + SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xfz", self.SRC_FILE)

    def configure(self):
        clang = cc(self)
        clang_cxx = cxx(self)
        with local.cwd(self.src_dir):
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure = local["./configure"]
                run(configure["--with-static-linked-ext", "--disable-shared"])

    def build(self):
        with local.cwd(self.src_dir):
            run(make["-j", CFG["jobs"]])

    def run_tests(self, runner):
        exp = wrap(path.join(self.src_dir, "ruby"), self)

        with local.env(RUBYOPT=""):
            run(ruby[path.join(self.testdir, "benchmark", "run.rb"),
                     "--ruby=\"" + str(exp) + "\"", "--opts=\"-I" + path.join(
                         self.testdir, "lib") + " -I" + path.join(
                             self.testdir, ".") + " -I" + path.join(
                                 self.testdir, ".ext", "common") + "\"", "-r"])
