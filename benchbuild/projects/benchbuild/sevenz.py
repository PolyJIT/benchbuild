from plumbum import local

from benchbuild import project
from benchbuild.downloads import HTTP
from benchbuild.utils.cmd import cp, make, tar
from benchbuild.utils import compiler, run, wrapping


class SevenZip(project.Project):
    """ 7Zip """

    NAME = '7z'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    VERSION = '16.02'
    SOURCE = [
        HTTP(remote={
            '16.02':
            'http://downloads.sourceforge.net/'
            'project/p7zip/p7zip/16.02/p7zip_16.02_src_all.tar.bz2'
        },
             local='p7zip.tar.bz2')
    ]

    def compile(self):
        sevenzip_source = local.path(self.source[0].local)
        unpack_dir = local.path('p7zip_{0}'.format(self.version))
        tar('xfj', sevenzip_source)

        cp(unpack_dir / "makefile.linux_clang_amd64_asm",
           unpack_dir / "makefile.machine")

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)

        with local.cwd(unpack_dir):
            make_ = run.watch(make)
            make_("CC=" + str(clang), "CXX=" + str(clang_cxx), "clean", "all")

    def run_tests(self):
        unpack_dir = local.path('p7zip_{0}'.format(self.version))
        _7z = wrapping.wrap(unpack_dir / "bin" / "7za", self)
        _7z = run.watch(_7z)
        _7z("b", "-mmt1")
