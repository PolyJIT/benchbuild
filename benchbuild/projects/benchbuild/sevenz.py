from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import HTTP
from benchbuild.utils.cmd import cp, make, tar


class SevenZip(bb.Project):
    """ 7Zip """

    NAME = '7z'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    SOURCE = [
        HTTP(
            remote={
                '16.02':
                    'http://downloads.sourceforge.net/'
                    'project/p7zip/p7zip/16.02/p7zip_16.02_src_all.tar.bz2'
            },
            local='p7zip.tar.bz2'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        sevenzip_source = local.path(self.source_of('p7zip.tar.bz2'))
        sevenzip_version = self.version_of('p7zip.tar.bz2')
        unpack_dir = local.path(f'p7zip_{sevenzip_version}')
        tar('xfj', sevenzip_source)

        cp(
            unpack_dir / "makefile.linux_clang_amd64_asm",
            unpack_dir / "makefile.machine"
        )

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)

        with local.cwd(unpack_dir):
            _make = bb.watch(make)
            _make("CC=" + str(clang), "CXX=" + str(clang_cxx), "clean", "all")

    def run_tests(self):
        sevenzip_version = self.version_of('p7zip.tar.bz2')
        unpack_dir = local.path(f'p7zip_{sevenzip_version}')
        _7z = bb.wrap(unpack_dir / "bin" / "7za", self)
        _7z = bb.watch(_7z)
        _7z("b", "-mmt1")
