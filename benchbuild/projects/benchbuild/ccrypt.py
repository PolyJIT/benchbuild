from os import path
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.wrapping import wrap
from benchbuild.utils.run import run
from benchbuild.utils.downloader import Wget
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.cmd import tar, make
from plumbum import local


class Ccrypt(BenchBuildGroup):
    """ ccrypt benchmark """

    NAME = 'ccrypt'
    DOMAIN = 'encryption'
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
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

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

    def run_tests(self, experiment, run):
        ccrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(ccrypt_dir):
            wrap(path.join(ccrypt_dir, "src", self.name), experiment)
            wrap(path.join(ccrypt_dir, "check", "crypt3-check"), experiment)
            wrap(path.join(ccrypt_dir, "check", "rijndael-check"), experiment)
            run(make["check"])
