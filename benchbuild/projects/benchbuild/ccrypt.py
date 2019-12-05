from plumbum import local
import benchbuild as bb

from benchbuild.downloads import HTTP
from benchbuild.utils.cmd import make, tar


class Ccrypt(bb.Project):
    """ ccrypt benchmark """

    NAME: str = 'ccrypt'
    DOMAIN: str = 'encryption'
    GROUP: str = 'benchbuild'
    VERSION: str = '1.10'
    SOURCE = [
        HTTP(remote={
            '1.10':
            "http://ccrypt.sourceforge.net/download/ccrypt-1.10.tar.gz"
        },
             local='ccrypt.tar.gz')
    ]

    def compile(self):
        ccrypt_source = bb.path(self.source_of('ccrypt.tar.gz'))
        tar('xfz', ccrypt_source)
        unpack_dir = 'ccrypt-{0}'.format(self.version)

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)

        with bb.cwd(unpack_dir):
            configure = local["./configure"]
            configure = bb.watch(configure)
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure()
            make_ = bb.watch(make)
            make_("check")

    def run_tests(self):
        unpack_dir = 'ccrypt-{0}'.format(self.version)
        with local.cwd(unpack_dir):
            bb.wrap(local.path("src") / self.name, self)
            bb.wrap(local.path("check") / "crypt3-check", self)
            bb.wrap(local.path("check") / "rijndael-check", self)

            make_ = bb.watch(make)
            make_("check")
