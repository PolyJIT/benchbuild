from plumbum import local

from benchbuild.project import Project
from benchbuild.environments import container
from benchbuild.source import HTTP
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make, ruby, tar


class Ruby(Project):
    NAME: str = 'ruby'
    DOMAIN: str = 'compilation'
    GROUP: str = 'benchbuild'
    SOURCE = [
        HTTP(remote={
            '2.7.0':
            'https://cache.ruby-lang.org/pub/ruby/2.7/ruby-2.7.0.tar.gz'
        },
             local='ruby.tar.gz'),
        HTTP(remote={
            '2016-11-ruby-inputs.tar.gz':
            'http://lairosiel.de/dist/2016-11-ruby-inputs.tar.gz'
        },
             local='inputs.tar.gz')
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def compile(self):
        ruby_source = local.path(self.source_of('ruby.tar.gz'))
        ruby_version = self.version_of('ruby.tar.gz')
        tar("xfz", ruby_source)
        unpack_dir = local.path(f'ruby-{ruby_version}')

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
        ruby_version = self.version_of('ruby.tar.gz')
        unpack_dir = local.path(f'ruby-{ruby_version}')
        ruby_n = wrapping.wrap(unpack_dir / "ruby", self)
        test_dir = local.path('./ruby/')

        with local.env(RUBYOPT=""):
            _ = run.watch(ruby)
            ruby(
                test_dir / "benchmark" / "run.rb",
                "--ruby=\"" + str(ruby_n) + "\"",
                "--opts=\"-I" + test_dir / "lib" + " -I" + test_dir / "." +
                " -I" + test_dir / ".ext" / "common" + "\"", "-r")
