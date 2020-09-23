from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.settings import CFG
from benchbuild.source import HTTP
from benchbuild.utils.cmd import make, ruby, tar
from benchbuild.utils.settings import get_number_of_jobs


class Ruby(bb.Project):
    NAME = 'ruby'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    SOURCE = [
        HTTP(
            remote={
                '2.2.2': (
                    'http://cache.ruby-lang.org/pub/ruby/2.2.2/'
                    'ruby-2.2.2.tar.gz'
                )
            },
            local='ruby.tar.gz'
        ),
        HTTP(
            remote={
                '2016-11-ruby-inputs.tar.gz':
                    'http://lairosiel.de/dist/2016-11-ruby-inputs.tar.gz'
            },
            local='inputs.tar.gz'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        ruby_source = local.path(self.source_of('ruby.tar.gz'))
        ruby_version = self.version_of('ruby.tar.gz')
        tar("xfz", ruby_source)
        unpack_dir = local.path(f'ruby-{ruby_version}')

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)
        with local.cwd(unpack_dir):
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure = local["./configure"]
                configure = bb.watch(configure)
                configure("--with-static-linked-ext", "--disable-shared")
            _make = bb.watch(make)
            _make("-j", get_number_of_jobs(CFG))

    def run_tests(self):
        ruby_version = self.version_of('ruby.tar.gz')
        unpack_dir = local.path(f'ruby-{ruby_version}')
        ruby_n = bb.wrap(unpack_dir / "ruby", self)
        test_dir = local.path('./ruby/')

        with local.env(RUBYOPT=""):
            _ = bb.watch(ruby)
            ruby(
                test_dir / "benchmark" / "run.rb",
                "--ruby=\"" + str(ruby_n) + "\"",
                "--opts=\"-I" + test_dir / "lib" + " -I" + test_dir / "." +
                " -I" + test_dir / ".ext" / "common" + "\"", "-r"
            )
