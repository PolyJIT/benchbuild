from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import with_wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_wget({
    "1.10": "http://ccrypt.sourceforge.net/download/ccrypt-1.10.tar.gz"
})
class Ccrypt(Project):
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

        clang = cc(self)
        clang_cxx = cxx(self)

        with local.cwd(unpack_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run(configure)
            run(make["check"])

    def run_tests(self, runner):
        unpack_dir = 'ccrypt-{0}'.format(self.version)
        with local.cwd(unpack_dir):
            wrap(path.join("src", self.name), self)
            wrap(path.join("check", "crypt3-check"), self)
            wrap(path.join("check", "rijndael-check"), self)
            run(make["check"])
