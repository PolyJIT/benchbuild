from plumbum import local

import benchbuild as bb
from benchbuild.settings import CFG
from benchbuild.utils import download
from benchbuild.utils.cmd import make, ruby, tar
from benchbuild.utils.settings import get_number_of_jobs


@download.with_wget(
    {'2.2.2': 'http://cache.ruby-lang.org/pub/ruby/2.2.2/ruby-2.2.2.tar.gz'})
class Ruby(bb.Project):
    NAME = 'ruby'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    VERSION = '2.2.2'
    SRC_FILE = 'ruby.tar.gz'

    def compile(self):
        self.download()
        tar("xfz", self.src_file)
        unpack_dir = bb.path('ruby-{0}'.format(self.version))

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)
        with bb.cwd(unpack_dir):
            with bb.env(CC=str(clang), CXX=str(clang_cxx)):
                configure = local["./configure"]
                configure = bb.watch(configure)
                configure("--with-static-linked-ext", "--disable-shared")
            _make = bb.watch(make)
            _make("-j", get_number_of_jobs(CFG))

    def run_tests(self):
        unpack_dir = bb.path('ruby-{0}'.format(self.version))
        testdir = bb.path(self.testdir)
        ruby_n = bb.wrap(unpack_dir / "ruby", self)

        with bb.env(RUBYOPT=""):
            _ = bb.watch(ruby)
            ruby(
                test_dir / "benchmark" / "run.rb",
                "--ruby=\"" + str(ruby_n) + "\"",
                "--opts=\"-I" + testdir / "lib" + " -I" + testdir / "." +
                " -I" + testdir / ".ext" / "common" + "\"", "-r")
