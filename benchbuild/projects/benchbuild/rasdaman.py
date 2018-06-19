from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import autoreconf, make
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import Git
from benchbuild.utils.run import run


class Rasdaman(Project):
    """ Rasdaman """

    NAME = 'Rasdaman'
    DOMAIN = 'database'
    GROUP = 'benchbuild'
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
        clang = cc(self)
        clang_cxx = cxx(self)

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

    def run_tests(self, runner):
        import logging
        log = logging.getLogger(__name__)
        log.warning('Not implemented')
