import logging

from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.settings import CFG
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Git
from benchbuild.utils.run import run
from benchbuild.utils.versions import get_version_from_cache_dir

from plumbum import local
from benchbuild.utils.cmd import autoreconf, make

from os import path


class Rasdaman(BenchBuildGroup):
    """ Rasdaman """

    NAME = 'Rasdaman'
    DOMAIN = 'database'
    SRC_FILE = 'rasdaman.git'
    

    src_uri = "git://rasdaman.org/rasdaman.git"

    gdal_dir = "gdal"
    gdal_uri = "https://github.com/OSGeo/gdal"

    def download(self):
        Git(self.gdal_uri, self.gdal_dir)
        Git(self.src_uri, self.SRC_FILE)

    def configure(self):
        rasdaman_dir = path.join(self.SRC_FILE)
        gdal_dir = path.join(self.gdal_dir, self.gdal_dir)
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        with local.cwd(gdal_dir):
            configure = local["./configure"]

            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run(configure["--with-pic", "--enable-static",
                              "--disable-debug", "--with-gnu-ld",
                              "--without-ld-shared", "--without-libtool"])
                run(make["-j", CFG["jobs"]])

        with local.cwd(rasdaman_dir):
            autoreconf("-i")
            configure = local["./configure"]

            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run(configure["--without-debug-symbols", "--enable-benchmark",
                              "--with-static-libs", "--disable-java",
                              "--with-pic", "--disable-debug",
                              "--without-docs"])

    def build(self):
        with local.cwd(self.SRC_FILE):
            run(make["clean", "all", "-j", CFG["jobs"]])

    def run_tests(self, experiment, run):
        log = logging.getLogger('benchbuild')
        log.warn('Not implemented')
