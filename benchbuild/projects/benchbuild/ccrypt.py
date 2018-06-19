from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class Ccrypt(Project):
    """ ccrypt benchmark """

    NAME = 'ccrypt'
    DOMAIN = 'encryption'
    GROUP = 'benchbuild'
    VERSION = '1.10'
    SRC_FILE = 'ccrypt-{0}.tar.gz'.format(VERSION)

    src_dir = "ccrypt-{0}".format(VERSION)
    src_uri = \
        "http://ccrypt.sourceforge.net/download/ccrypt-{0}.tar.gz".format(
            VERSION)

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar('xfz', path.join(self.builddir, self.SRC_FILE))

    def configure(self):
        clang = cc(self)
        clang_cxx = cxx(self)

        ccrypt_dir = path.join('.', self.src_dir)
        with local.cwd(ccrypt_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang),
                           CXX=str(clang_cxx)):
                run(configure)

    def build(self):
        ccrypt_dir = path.join('.', self.src_dir)
        with local.cwd(ccrypt_dir):
            run(make["check"])

    def run_tests(self, runner):
        ccrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(ccrypt_dir):
            wrap(path.join(ccrypt_dir, "src", self.name), self)
            wrap(path.join(ccrypt_dir, "check", "crypt3-check"), self)
            wrap(path.join(ccrypt_dir, "check", "rijndael-check"), self)
            run(make["check"])
