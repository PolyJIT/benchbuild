from plumbum import local

import benchbuild as bb

from benchbuild.downloads import HTTP
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make, ruby, tar


class Ruby(bb.Project):
    NAME: str = 'ruby'
    DOMAIN: str = 'compilation'
    GROUP: str = 'benchbuild'
    VERSION: str = '2.2.2'
    SOURCE = [
        HTTP(remote={
            '2.2.2':
            'http://cache.ruby-lang.org/pub/ruby/2.2.2/ruby-2.2.2.tar.gz'
        },
             local='ruby.tar.gz'),
        HTTP(remote={
            '2016-11-ruby-inputs.tar.gz':
            'http://lairosiel.de/dist/2016-11-ruby-inputs.tar.gz'
        },
             local='inputs.tar.gz')
    ]

    def compile(self):
        ruby_source = bb.path(self.source_of('ruby.tar.gz')) 
        tar("xfz", ruby_source)
        unpack_dir = bb.path('ruby-{0}'.format(self.version))

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)
        with local.cwd(unpack_dir):
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure = local["./configure"]
                configure = bb.watch(configure)
                configure("--with-static-linked-ext", "--disable-shared")
            make_ = bb.watch(make)
            make_("-j", CFG["jobs"])

    def run_tests(self):
        unpack_dir = bb.path('ruby-{0}'.format(self.version))
        ruby_n = bb.wrap(unpack_dir / "ruby", self)
        test_dir = bb.path('./ruby/')

        with bb.env(RUBYOPT=""):
            ruby_ = bb.watch(ruby)
            ruby(
                test_dir / "benchmark" / "run.rb",
                "--ruby=\"" + str(ruby_n) + "\"",
                "--opts=\"-I" + test_dir / "lib" + " -I" + test_dir / "." +
                " -I" + test_dir / ".ext" / "common" + "\"", "-r")
