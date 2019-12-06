from functools import partial

from plumbum import local

import benchbuild as bb

from benchbuild.downloads import Git
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make, mkdir, tar


class SpiderMonkey(bb.Project):
    """
    SpiderMonkey requires a legacy version of autoconf: autoconf-2.13
    """

    NAME = 'js'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    SOURCE = [
        Git(remote='https://gitub.com/mozilla/gecko-dev.git',
            local='gecko-dev.git',
            limit=5,
            refspec='HEAD')
    ]

    def compile(self):
        gecko_repo = bb.path(self.source_of('gecko-dev.git'))

        js_dir = gecko_repo / "js" / "src"
        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)
        with bb.cwd(js_dir):
            make_src_pkg = local["./make-source-package.sh"]
            with bb.env(DIST=self.builddir,
                           MOZJS_MAJOR_VERSION=0,
                           MOZJS_MINOR_VERSION=0,
                           MOZJS_PATCH_VERSION=0):
                make_src_pkg()

        mozjs_dir = bb.path("mozjs-0.0.0")
        mozjs_src_dir = mozjs_dir / "js" / "src"
        tar("xfj", mozjs_dir + ".tar.bz2")
        with bb.cwd(mozjs_src_dir):
            mkdir("obj")
            autoconf = local["autoconf-2.13"]
            autoconf()
            with bb.cwd("obj"):
                with bb.env(CC=str(clang), CXX=str(clang_cxx)):
                    configure = local["../configure"]
                    configure = bb.watch(configure)
                    configure('--without-system-zlib')

        mozjs_obj_dir = mozjs_src_dir / "obj"
        with bb.cwd(mozjs_obj_dir):
            make_ = bb.watch(make)
            make_("-j", str(CFG["jobs"]))

    def run_tests(self):
        mozjs_obj_dir = bb.path("mozjs-0.0.0") / "js" / "src" / "obj"
        self.runtime_extension = partial(self, may_wrap=False)
        bb.wrap(mozjs_obj_dir / "js" / "src" / "shell" / "js", self)

        with bb.cwd(mozjs_obj_dir):
            make_ = bb.watch(make)
            make_("check-jstests")
