from benchbuild.project import Project
from benchbuild.environments import container
from benchbuild.source import HTTP
from benchbuild.utils.cmd import cp, make, tar


class SevenZip(Project):
    """ 7Zip """

    NAME: str = '7z'
    DOMAIN: str = 'compression'
    GROUP: str = 'benchbuild'
    SOURCE: str = [
        HTTP(remote={
            '16.02':
            'http://downloads.sourceforge.net/'
            'project/p7zip/p7zip/16.02/p7zip_16.02_src_all.tar.bz2'
        },
             local='p7zip.tar.bz2')
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def compile(self):
        sevenzip_source = local.path(self.source_of('p7zip.tar.bz2'))
        sevenzip_version = self.version_of('p7zip.tar.bz2')
        unpack_dir = local.path(f'p7zip_{sevenzip_version}')
        tar('xfj', sevenzip_source)

        cp(unpack_dir / "makefile.linux_clang_amd64_asm",
           unpack_dir / "makefile.machine")

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)

        with local.cwd(unpack_dir):
            make_ = run.watch(make)
            make_("CC=" + str(clang), "CXX=" + str(clang_cxx), "clean", "all")

    def run_tests(self):
        sevenzip_version = self.version_of('p7zip.tar.bz2')
        unpack_dir = local.path(f'p7zip_{sevenzip_version}')
        _7z = wrapping.wrap(unpack_dir / "bin" / "7za", self)
        _7z = run.watch(_7z)
        _7z("b", "-mmt1")
