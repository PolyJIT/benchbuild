from plumbum import local

from benchbuild.project import Project
from benchbuild.environments import container
from benchbuild.source import Git
from benchbuild.settings import CFG
from benchbuild.utils.cmd import autoreconf, make


class Rasdaman(Project):
    """ Rasdaman """

    NAME: str = 'rasdaman'
    DOMAIN: str = 'database'
    GROUP: str = 'benchbuild'
    SOURCE = [
        Git(remote='git://rasdaman.org/rasdaman.git',
            local='rasdaman.git',
            limit=5,
            refspec='HEAD'),
        Git(remote='https://github.com/OSGeo/gdal',
            local='gdal.git',
            limit=5,
            refspec='HEAD')
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    gdal_dir = "gdal"
    gdal_uri = "https://github.com/OSGeo/gdal"

    def compile(self):
        rasdaman_repo = local.path(self.source_of('rasdaman.git'))
        gdal_repo = local.path(self.source_of('gdal.git'))

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)

        with local.cwd(gdal_repo):
            configure = local["./configure"]
            configure = run.watch(configure)

            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure("--with-pic", "--enable-static", "--disable-debug",
                          "--with-gnu-ld", "--without-ld-shared",
                          "--without-libtool")
                make_ = run.watch(make)
                make_("-j", CFG["jobs"])

        with local.cwd(rasdaman_repo):
            autoreconf("-i")
            configure = local["./configure"]
            configure = run.watch(configure)

            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure("--without-debug-symbols", "--enable-benchmark",
                          "--with-static-libs", "--disable-java", "--with-pic",
                          "--disable-debug", "--without-docs")
            make_ = run.watch(make)
            make_("clean", "all", "-j", CFG["jobs"])

    def run_tests(self):
        import logging
        log = logging.getLogger(__name__)
        log.warning('Not implemented')
