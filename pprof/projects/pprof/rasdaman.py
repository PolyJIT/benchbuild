#!/usr/bin/evn python
#

from pprof.project import ProjectFactory
from pprof.settings import config
from pprof.projects.pprof.group import PprofGroup

from os import path
from plumbum import local


# git clone git://rasdaman.org/rasdaman.git
class Rasdaman(PprofGroup):
    """ Rasdaman """

    NAME = 'Rasdaman'
    DOMAIN = 'database'

    class Factory:
        def create(self, exp):
            return Rasdaman(exp, "Rasdaman", "database")

    ProjectFactory.addFactory("Rasdaman", Factory())

    src_dir = "rasdaman.git"
    src_uri = "git://rasdaman.org/rasdaman.git"

    gdal_dir = "gdal"
    gdal_uri = "https://github.com/OSGeo/gdal"

    def download(self):
        from pprof.utils.downloader import Git

        with local.cwd(self.builddir):
            Git(self.gdal_uri, self.gdal_dir)
            Git(self.src_uri, self.src_dir)

    def configure(self):
        from pprof.utils.compiler import lt_clang, lt_clang_cxx
        from pprof.utils.run import run
        from plumbum.cmd import autoreconf, make
        rasdaman_dir = path.join(self.builddir, self.src_dir)
        gdal_dir = path.join(self.builddir, self.gdal_dir, self.gdal_dir)
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                     self.compiler_extension)

        with local.cwd(gdal_dir):
            configure = local["./configure"]

            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run(configure["--with-pic", "--enable-static",
                              "--disable-debug", "--with-gnu-ld",
                              "--without-ld-shared", "--without-libtool"])
                run(make["-j", config["jobs"]])

        with local.cwd(rasdaman_dir):
            autoreconf("-i")
            configure = local["./configure"]

            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run(configure["--without-debug-symbols", "--enable-benchmark",
                              "--with-static-libs", "--disable-java",
                              "--with-pic", "--disable-debug",
                              "--without-docs"])

    def build(self):
        from plumbum.cmd import make
        from pprof.utils.run import run

        rasdaman_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(rasdaman_dir):
            run(make["clean", "all", "-j", config["jobs"]])

    def run_tests(self, experiment):
        from pprof.project import wrap
        rasdaman_dir = path.join(self.builddir, self.src_dir)
        pass
