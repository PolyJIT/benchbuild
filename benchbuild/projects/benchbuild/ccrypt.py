from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import HTTP
from benchbuild.utils.cmd import make, tar


class Ccrypt(bb.Project):
    """ ccrypt benchmark """

    NAME = 'ccrypt'
    DOMAIN = 'encryption'
    GROUP = 'benchbuild'
    SOURCE = [
        HTTP(
            remote={
                '1.10':
                    "http://ccrypt.sourceforge.net/download/ccrypt-1.10.tar.gz"
            },
            local='ccrypt.tar.gz'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        ccrypt_source = local.path(self.source_of('ccrypt.tar.gz'))
        ccrypt_version = self.version_of('ccrypt.tar.gz')
        tar('xfz', ccrypt_source)
        unpack_dir = f'ccrypt-{ccrypt_version}'

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)

        with local.cwd(unpack_dir):
            configure = local["./configure"]
            _configure = bb.watch(configure)
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                _configure()
            _make = bb.watch(make)
            _make("check")

    def run_tests(self):
        ccrypt_version = self.version_of('ccrypt.tar.gz')
        unpack_dir = f'ccrypt-{ccrypt_version}'
        with local.cwd(unpack_dir):
            bb.wrap(local.path("src") / self.name, self)
            bb.wrap(local.path("check") / "crypt3-check", self)
            bb.wrap(local.path("check") / "rijndael-check", self)

            _make = bb.watch(make)
            _make("check")
