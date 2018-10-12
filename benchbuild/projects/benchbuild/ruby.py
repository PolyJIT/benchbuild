from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make, ruby, tar
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import with_wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_wget({
    '2.2.2':
    'http://cache.ruby-lang.org/pub/ruby/2.2.2/ruby-2.2.2.tar.gz'
})
class Ruby(Project):
    NAME = 'ruby'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    VERSION = '2.2.2'
    SRC_FILE = 'ruby.tar.gz'

    def compile(self):
        self.download()
        tar("xfz", self.src_file)
        unpack_dir = local.path('ruby-{0}'.format(self.version))

        clang = cc(self)
        clang_cxx = cxx(self)
        with local.cwd(unpack_dir):
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure = local["./configure"]
                run(configure["--with-static-linked-ext", "--disable-shared"])
            run(make["-j", CFG["jobs"]])

    def run_tests(self, runner):
        unpack_dir = local.path('ruby-{0}'.format(self.version))
        ruby_n = wrap(unpack_dir / "ruby", self)
        testdir = local.path(self.testdir)

        with local.env(RUBYOPT=""):
            run(ruby[testdir / "benchmark" / "run.rb", "--ruby=\"" +
                     str(ruby_n) + "\"", "--opts=\"-I" + testdir / "lib" +
                     " -I" + testdir / "." + " -I" +
                     testdir / ".ext" / "common" + "\"", "-r"])
