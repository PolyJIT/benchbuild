from plumbum import local

from benchbuild.project import Project

from benchbuild.environments import container
from benchbuild.source import HTTP
from benchbuild.utils.cmd import make, tar


class Ccrypt(Project):
    """ ccrypt benchmark """

    NAME: str = 'ccrypt'
    DOMAIN: str = 'encryption'
    GROUP: str = 'benchbuild'
    SOURCE = [
        HTTP(remote={
            '1.11':
            "http://ccrypt.sourceforge.net/download/1.11/ccrypt-1.11.tar.gz"
        },
             local='ccrypt.tar.gz')
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def compile(self):
        ccrypt_source = local.path(self.source_of('ccrypt.tar.gz'))
        ccrypt_version = self.version_of('ccrypt.tar.gz')
        tar('xfz', ccrypt_source)
        unpack_dir = f'ccrypt-{ccrypt_version}'

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
        ccrypt_version = self.version_of('ccrypt.tar.gz')
        unpack_dir = f'ccrypt-{ccrypt_version}'
        with local.cwd(unpack_dir):
            wrapping.wrap(local.path("src") / self.name, self)
            wrapping.wrap(local.path("check") / "crypt3-check", self)
            wrapping.wrap(local.path("check") / "rijndael-check", self)

            make_ = run.watch(make)
            make_("check")
