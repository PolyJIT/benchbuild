from plumbum import local

import benchbuild as bb
from benchbuild.source import HTTP
from benchbuild.utils.cmd import make, tar


class Ccrypt(bb.Project):
    """ ccrypt benchmark """

    NAME = 'ccrypt'
    DOMAIN = 'encryption'
    GROUP = 'benchbuild'
    SOURCE = [
        HTTP(remote={
            '1.10': "http://ccrypt.sourceforge.net/download/ccrypt-1.10.tar.gz"
        },
             local='ccrypt.tar.gz')
    ]

    def compile(self):
        ccrypt_source = bb.path(self.source_of('ccrypt.tar.gz'))
        ccrypt_version = self.version_of('ccrypt.tar.gz')
        tar('xfz', ccrypt_source)
        unpack_dir = f'ccrypt-{ccrypt_version}'

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)

        with bb.cwd(unpack_dir):
            configure = local["./configure"]
            _configure = bb.watch(configure)
            with bb.env(CC=str(clang), CXX=str(clang_cxx)):
                _configure()
            _make = bb.watch(make)
            _make("check")

    def run_tests(self):
        ccrypt_version = self.version_of('ccrypt.tar.gz')
        unpack_dir = f'ccrypt-{ccrypt_version}'
        with bb.cwd(unpack_dir):
            bb.wrap(bb.path("src") / self.name, self)
            bb.wrap(bb.path("check") / "crypt3-check", self)
            bb.wrap(bb.path("check") / "rijndael-check", self)

            _make = bb.watch(make)
            _make("check")
