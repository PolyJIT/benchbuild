from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import cp, make, tar
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import with_wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_wget({
    '16.02':
    'http://downloads.sourceforge.net/project/p7zip/p7zip/16.02/p7zip_16.02_src_all.tar.bz2'
})
class SevenZip(Project):
    """ 7Zip """

    NAME = '7z'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    VERSION = '16.02'
    SRC_FILE = 'p7zip.tar.bz2'

    def compile(self):
        self.download()
        unpack_dir = local.path('p7zip_{0}'.format(self.version))
        tar('xfj', self.src_file)

        cp(unpack_dir / "makefile.linux_clang_amd64_asm",
           unpack_dir / "makefile.machine")

        clang = cc(self)
        clang_cxx = cxx(self)

        with local.cwd(unpack_dir):
            run(make["CC=" + str(clang), "CXX=" +
                     str(clang_cxx), "clean", "all"])

    def run_tests(self, runner):
        unpack_dir = local.path('p7zip_{0}'.format(self.version))
        _7z = wrap(unpack_dir / "bin" / "7za", self)
        runner(_7z["b", "-mmt1"])
