from functools import partial

from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.settings import CFG
from benchbuild.source import Git
from benchbuild.utils.cmd import make, mkdir, tar
from benchbuild.utils.settings import get_number_of_jobs


class SpiderMonkey(bb.Project):
    """
    SpiderMonkey requires a legacy version of autoconf: autoconf-2.13
    """

    NAME = 'js'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    SOURCE = [
        Git(
            remote='https://github.com/mozilla/gecko-dev.git',
            local='gecko-dev.git',
            limit=5,
            refspec='HEAD'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        gecko_repo = local.path(self.source_of('gecko-dev.git'))

        js_dir = gecko_repo / "js" / "src"
        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)
        with local.cwd(js_dir):
            make_src_pkg = local["./make-source-package.sh"]
            with local.env(
                DIST=self.builddir,
                MOZJS_MAJOR_VERSION=0,
                MOZJS_MINOR_VERSION=0,
                MOZJS_PATCH_VERSION=0
            ):
                make_src_pkg()

        mozjs_dir = local.path("mozjs-0.0.0")
        mozjs_src_dir = mozjs_dir / "js" / "src"
        tar("xfj", mozjs_dir + ".tar.bz2")
        with local.cwd(mozjs_src_dir):
            mkdir("obj")
            autoconf = local["autoconf-2.13"]
            autoconf()
            with local.cwd("obj"):
                with local.env(CC=str(clang), CXX=str(clang_cxx)):
                    configure = local["../configure"]
                    _configure = bb.watch(configure)
                    _configure('--without-system-zlib')

        mozjs_obj_dir = mozjs_src_dir / "obj"
        with local.cwd(mozjs_obj_dir):
            _make = bb.watch(make)
            _make("-j", get_number_of_jobs(CFG))

    def run_tests(self):
        mozjs_obj_dir = local.path("mozjs-0.0.0") / "js" / "src" / "obj"
        self.runtime_extension = partial(self, may_wrap=False)
        bb.wrap(mozjs_obj_dir / "js" / "src" / "shell" / "js", self)

        with local.cwd(mozjs_obj_dir):
            _make = bb.watch(make)
            _make("check-jstests")
