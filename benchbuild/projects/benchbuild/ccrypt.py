from plumbum import local

import benchbuild as bb
from benchbuild.utils import download
from benchbuild.utils.cmd import make, tar


@download.with_wget(
    {"1.10": "http://ccrypt.sourceforge.net/download/ccrypt-1.10.tar.gz"})
class Ccrypt(bb.Project):
    """ ccrypt benchmark """

    NAME = 'ccrypt'
    DOMAIN = 'encryption'
    GROUP = 'benchbuild'
    VERSION = '1.10'
    SRC_FILE = 'ccrypt.tar.gz'

    def compile(self):
        self.download()
        tar('xfz', self.src_file)
        unpack_dir = 'ccrypt-{0}'.format(self.version)

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
        unpack_dir = 'ccrypt-{0}'.format(self.version)
        with bb.cwd(unpack_dir):
            bb.wrap(bb.path("src") / self.name, self)
            bb.wrap(bb.path("check") / "crypt3-check", self)
            bb.wrap(bb.path("check") / "rijndael-check", self)

            _make = bb.watch(make)
            _make("check")
