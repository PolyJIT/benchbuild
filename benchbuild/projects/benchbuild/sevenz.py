from plumbum import local

from benchbuild import project
from benchbuild.utils.cmd import cp, make, tar
from benchbuild.utils import compiler, download, run, wrapping


@download.with_wget({
    '16.02':
    'http://downloads.sourceforge.net/'
    'project/p7zip/p7zip/16.02/p7zip_16.02_src_all.tar.bz2'
})
class SevenZip(project.Project):
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

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)

        with local.cwd(unpack_dir):
            run.run(make["CC=" + str(clang), "CXX=" +
                         str(clang_cxx), "clean", "all"])

    def run_tests(self, runner):
        unpack_dir = local.path('p7zip_{0}'.format(self.version))
        _7z = wrapping.wrap(unpack_dir / "bin" / "7za", self)
        runner(_7z["b", "-mmt1"])
