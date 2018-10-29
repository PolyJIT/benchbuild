from plumbum import local

from benchbuild import project
from benchbuild.settings import CFG
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make, ruby, tar


@download.with_wget({
    '2.2.2':
    'http://cache.ruby-lang.org/pub/ruby/2.2.2/ruby-2.2.2.tar.gz'
})
class Ruby(project.Project):
    NAME = 'ruby'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    VERSION = '2.2.2'
    SRC_FILE = 'ruby.tar.gz'

    def compile(self):
        self.download()
        tar("xfz", self.src_file)
        unpack_dir = local.path('ruby-{0}'.format(self.version))

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)
        with local.cwd(unpack_dir):
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure = local["./configure"]
                run.run(
                    configure["--with-static-linked-ext", "--disable-shared"])
            run.run(make["-j", CFG["jobs"]])

    def run_tests(self, runner):
        unpack_dir = local.path('ruby-{0}'.format(self.version))
        ruby_n = wrapping.wrap(unpack_dir / "ruby", self)
        testdir = local.path(self.testdir)

        with local.env(RUBYOPT=""):
            run.run(ruby[testdir / "benchmark" / "run.rb", "--ruby=\"" +
                         str(ruby_n) + "\"", "--opts=\"-I" + testdir / "lib" +
                         " -I" + testdir / "." + " -I" +
                         testdir / ".ext" / "common" + "\"", "-r"])
