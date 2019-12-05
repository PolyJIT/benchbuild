from plumbum import local

import benchbuild as bb

from benchbuild.downloads import HTTP
from benchbuild.utils.cmd import cp, make, tar


class SevenZip(bb.Project):
    """ 7Zip """

    NAME: str = '7z'
    DOMAIN: str = 'compression'
    GROUP: str = 'benchbuild'
    VERSION: str = '16.02'
    SOURCE: str = [
        HTTP(remote={
            '16.02':
            'http://downloads.sourceforge.net/'
            'project/p7zip/p7zip/16.02/p7zip_16.02_src_all.tar.bz2'
        },
             local='p7zip.tar.bz2')
    ]

    def compile(self):
        sevenzip_source = local.path(self.source[0].local)
        sevenzip_source = bb.path(self.source_of('p7zip.tar.bz2'))
        unpack_dir = bb.path('p7zip_{0}'.format(self.version))
        tar('xfj', sevenzip_source)

        cp(unpack_dir / "makefile.linux_clang_amd64_asm",
           unpack_dir / "makefile.machine")

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)

        with bb.cwd(unpack_dir):
            make_ = bb.watch(make)
            make_("CC=" + str(clang), "CXX=" + str(clang_cxx), "clean", "all")

    def run_tests(self):
        unpack_dir = local.path('p7zip_{0}'.format(self.version))
        _7z = bb.wrap(unpack_dir / "bin" / "7za", self)
        _7z = bb.watch(_7z)
        _7z("b", "-mmt1")
