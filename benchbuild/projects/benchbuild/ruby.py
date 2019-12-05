from plumbum import local

from benchbuild import project
from benchbuild.downloads import HTTP
from benchbuild.settings import CFG
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import make, ruby, tar


class Ruby(project.Project):
    VERSION = '2.2.2'
    NAME: str = 'ruby'
    DOMAIN: str = 'compilation'
    GROUP: str = 'benchbuild'
    SOURCE = [
        HTTP(remote={
            '2.2.2':
            'http://cache.ruby-lang.org/pub/ruby/2.2.2/ruby-2.2.2.tar.gz'
        },
             local='ruby.tar.gz')
    ]

    def compile(self):
        ruby_source = local.path(self.source[0].local)
        tar("xfz", ruby_source)
        unpack_dir = local.path('ruby-{0}'.format(self.version))

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)
        with local.cwd(unpack_dir):
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure = local["./configure"]
                configure = run.watch(configure)
                configure("--with-static-linked-ext", "--disable-shared")
            make_ = run.watch(make)
            make_("-j", CFG["jobs"])

    def run_tests(self):
        unpack_dir = local.path('ruby-{0}'.format(self.version))
        ruby_n = wrapping.wrap(unpack_dir / "ruby", self)
        testdir = local.path(self.testdir)

        with local.env(RUBYOPT=""):
            ruby_ = run.watch(ruby)
            ruby(
                testdir / "benchmark" / "run.rb",
                "--ruby=\"" + str(ruby_n) + "\"",
                "--opts=\"-I" + testdir / "lib" + " -I" + testdir / "." +
                " -I" + testdir / ".ext" / "common" + "\"", "-r")
