from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make, tar


@download.with_wget({
    "1.10":
    "http://ccrypt.sourceforge.net/download/ccrypt-1.10.tar.gz"
})
class Ccrypt(project.Project):
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

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)

        with local.cwd(unpack_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run.run(configure)
            run.run(make["check"])

    def run_tests(self, runner):
        unpack_dir = 'ccrypt-{0}'.format(self.version)
        with local.cwd(unpack_dir):
            wrapping.wrap(local.path("src") / self.name, self)
            wrapping.wrap(local.path("check") / "crypt3-check", self)
            wrapping.wrap(local.path("check") / "rijndael-check", self)
            run.run(make["check"])
