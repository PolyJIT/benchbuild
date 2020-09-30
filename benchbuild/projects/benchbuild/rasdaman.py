import logging

from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.settings import CFG
from benchbuild.source import Git
from benchbuild.utils.cmd import autoreconf, make
from benchbuild.utils.settings import get_number_of_jobs


class Rasdaman(bb.Project):
    """ Rasdaman """

    NAME = 'Rasdaman'
    DOMAIN = 'database'
    GROUP = 'benchbuild'
    SOURCE = [
        Git(
            remote='git://rasdaman.org/rasdaman.git',
            local='rasdaman.git',
            limit=5,
            refspec='HEAD'
        ),
        Git(
            remote='https://github.com/OSGeo/gdal',
            local='gdal.git',
            limit=5,
            refspec='HEAD'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    gdal_dir = "gdal"
    gdal_uri = "https://github.com/OSGeo/gdal"

    def compile(self):
        rasdaman_repo = local.path(self.source_of('rasdaman.git'))
        gdal_repo = local.path(self.source_of('gdal.git'))

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)

        with local.cwd(gdal_repo):
            configure = local["./configure"]
            _configure = bb.watch(configure)

            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                _configure(
                    "--with-pic", "--enable-static", "--with-gnu-ld",
                    "--without-ld-shared", "--without-libtool"
                )
                _make = bb.watch(make)
                _make("-j", get_number_of_jobs(CFG))

        with local.cwd(rasdaman_repo):
            autoreconf("-i")
            configure = local["./configure"]
            _configure = bb.watch(configure)

            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                _configure(
                    "--without-debug-symbols", "--with-static-libs",
                    "--disable-java", "--with-pic", "--disable-debug",
                    "--without-docs"
                )
            _make = bb.watch(make)
            _make("clean", "all", "-j", get_number_of_jobs(CFG))

    def run_tests(self):
        log = logging.getLogger(__name__)
        log.warning('Not implemented')
