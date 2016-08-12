from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.project import wrap
from benchbuild.utils.run import run
from benchbuild.utils.downloader import Wget
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from os import path
from plumbum import local
from benchbuild.utils.cmd import ln, tar, make


class Ccrypt(BenchBuildGroup):
    """ ccrypt benchmark """

    NAME = 'ccrypt'
    DOMAIN = 'encryption'
    VERSION = '1.10'
    SRC_FILE = 'ccrypt-{0}.tar.gz'.format(VERSION)

    check_f = "check"

    def prepare(self):
        super(Ccrypt, self).prepare()
        check_f = path.join(self.testdir, self.check_f)
        ln("-s", check_f, path.join(self.builddir, self.check_f))

    src_dir = "ccrypt-{0}".format(VERSION)
    src_uri = "http://ccrypt.sourceforge.net/download/ccrypt-{0}.tar.gz".format(VERSION)

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
                           CXX=str(clang_cxx),
                           LDFLAGS=" ".join(self.ldflags)):
                run(configure)

    def build(self):
        ccrypt_dir = path.join('.', self.src_dir)
        with local.cwd(ccrypt_dir):
            run(make["check"])

    def run_tests(self, experiment):
        ccrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(ccrypt_dir):
            wrap(path.join(ccrypt_dir, "src", self.name), experiment)
            wrap(path.join(ccrypt_dir, "check", "crypt3-check"), experiment)
            wrap(path.join(ccrypt_dir, "check", "rijndael-check"), experiment)
            run(make["check"])
