import benchbuild as bb
from benchbuild.utils import download
from benchbuild.utils.cmd import cp, make, tar


@download.with_wget({
    '16.02': 'http://downloads.sourceforge.net/'
             'project/p7zip/p7zip/16.02/p7zip_16.02_src_all.tar.bz2'
})
class SevenZip(bb.Project):
    """ 7Zip """

    NAME = '7z'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    VERSION = '16.02'
    SRC_FILE = 'p7zip.tar.bz2'

    def compile(self):
        self.download()
        unpack_dir = bb.path('p7zip_{0}'.format(self.version))
        tar('xfj', self.src_file)

        cp(unpack_dir / "makefile.linux_clang_amd64_asm",
           unpack_dir / "makefile.machine")

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)

        with bb.cwd(unpack_dir):
            _make = bb.watch(make)
            _make("CC=" + str(clang), "CXX=" + str(clang_cxx), "clean", "all")

    def run_tests(self):
        unpack_dir = bb.path('p7zip_{0}'.format(self.version))
        _7z = bb.wrap(unpack_dir / "bin" / "7za", self)
        _7z = bb.watch(_7z)
        _7z("b", "-mmt1")
