from plumbum import local

import benchbuild as bb
from benchbuild.settings import CFG
from benchbuild.utils import download
from benchbuild.utils.cmd import autoreconf, make
from benchbuild.utils.settings import get_number_of_jobs


@download.with_git('git://rasdaman.org/rasdaman.git', limit=5)
class Rasdaman(bb.Project):
    """ Rasdaman """

    NAME = 'Rasdaman'
    DOMAIN = 'database'
    GROUP = 'benchbuild'
    SRC_FILE = 'rasdaman.git'
    VERSION = 'HEAD'

    gdal_dir = "gdal"
    gdal_uri = "https://github.com/OSGeo/gdal"

    def compile(self):
        self.download()
        download.Git(self.gdal_uri, self.gdal_dir)
        rasdaman_dir = bb.path(self.src_file)
        gdal_dir = bb.path(self.gdal_dir) / self.gdal_dir

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)

        with bb.cwd(gdal_dir):
            configure = local["./configure"]
            _configure = bb.watch(configure)

            with bb.env(CC=str(clang), CXX=str(clang_cxx)):
                _configure("--with-pic", "--enable-static", "--with-gnu-ld",
                           "--without-ld-shared", "--without-libtool")
                _make = bb.watch(make)
                _make("-j", get_number_of_jobs(CFG))

        with bb.cwd(rasdaman_repo):
            autoreconf("-i")
            configure = local["./configure"]
            _configure = bb.watch(configure)

            with bb.env(CC=str(clang), CXX=str(clang_cxx)):
                _configure("--without-debug-symbols", "--with-static-libs",
                           "--disable-java", "--with-pic", "--disable-debug",
                           "--without-docs")
            _make = bb.watch(make)
            _make("clean", "all", "-j", get_number_of_jobs(CFG))

    def run_tests(self):
        import logging
        log = logging.getLogger(__name__)
        log.warning('Not implemented')
