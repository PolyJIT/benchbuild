from plumbum import local

from benchbuild import project
from benchbuild.downloads import HTTP
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import make, tar


class Ccrypt(project.Project):
    """ ccrypt benchmark """

    VERSION = '1.10'
    NAME: str = 'ccrypt'
    DOMAIN: str = 'encryption'
    GROUP: str = 'benchbuild'
    SOURCE = [
        HTTP(remote={
            '1.10':
            "http://ccrypt.sourceforge.net/download/ccrypt-1.10.tar.gz"
        },
             local='ccrypt.tar.gz')
    ]

    def compile(self):
        ccrypt_source = local.path(self.source[0].local)
        tar('xfz', ccrypt_source)
        unpack_dir = 'ccrypt-{0}'.format(self.version)

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)

        with local.cwd(unpack_dir):
            configure = local["./configure"]
            configure = run.watch(configure)
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure()
            make_ = run.watch(make)
            make_("check")

    def run_tests(self):
        unpack_dir = 'ccrypt-{0}'.format(self.version)
        with local.cwd(unpack_dir):
            wrapping.wrap(local.path("src") / self.name, self)
            wrapping.wrap(local.path("check") / "crypt3-check", self)
            wrapping.wrap(local.path("check") / "rijndael-check", self)

            make_ = run.watch(make)
            make_("check")
