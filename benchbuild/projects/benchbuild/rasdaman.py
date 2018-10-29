from plumbum import local

from benchbuild import project
from benchbuild.settings import CFG
from benchbuild.utils import compiler, download, run
from benchbuild.utils.cmd import autoreconf, make


@download.with_git('git://rasdaman.org/rasdaman.git', limit=5)
class Rasdaman(project.Project):
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
        rasdaman_dir = local.path(self.src_file)
        gdal_dir = local.path(self.gdal_dir) / self.gdal_dir

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)

        with local.cwd(gdal_dir):
            configure = local["./configure"]

            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run.run(configure["--with-pic", "--enable-static",
                                  "--disable-debug", "--with-gnu-ld",
                                  "--without-ld-shared", "--without-libtool"])
                run.run(make["-j", CFG["jobs"]])

        with local.cwd(rasdaman_dir):
            autoreconf("-i")
            configure = local["./configure"]

            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run.run(configure["--without-debug-symbols",
                                  "--enable-benchmark", "--with-static-libs",
                                  "--disable-java", "--with-pic",
                                  "--disable-debug", "--without-docs"])
            run.run(make["clean", "all", "-j", CFG["jobs"]])

    def run_tests(self, runner):
        import logging
        log = logging.getLogger(__name__)
        log.warning('Not implemented')
