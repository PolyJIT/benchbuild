from functools import partial

from plumbum import local

from benchbuild import project
from benchbuild.settings import CFG
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make, mkdir, tar


@download.with_git(
    "https://github.com/mozilla/gecko-dev.git",
    target_dir="gecko-dev.git",
    clone=False,
    limit=5)
class SpiderMonkey(project.Project):
    """
    SpiderMonkey requires a legacy version of autoconf: autoconf-2.13
    """

    NAME = 'js'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    VERSION = 'HEAD'
    SRC_FILE = "gecko-dev.git"

    src_uri = "https://github.com/mozilla/gecko-dev.git"

    def compile(self):
        self.download()

        js_dir = local.path(self.src_file) / "js" / "src"
        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)
        with local.cwd(js_dir):
            make_src_pkg = local["./make-source-package.sh"]
            with local.env(
                    DIST=self.builddir,
                    MOZJS_MAJOR_VERSION=0,
                    MOZJS_MINOR_VERSION=0,
                    MOZJS_PATCH_VERSION=0):
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
                    configure = configure["--without-system-zlib"]
                    run.run(configure)

        mozjs_obj_dir = mozjs_src_dir / "obj"
        with local.cwd(mozjs_obj_dir):
            run.run(make["-j", str(CFG["jobs"])])

    def run_tests(self, runner):
        mozjs_obj_dir = local.path("mozjs-0.0.0") / "js" / "src" / "obj"
        self.runtime_extension = partial(self, may_wrap=False)
        wrapping.wrap(mozjs_obj_dir / "js" / "src" / "shell" / "js", self)

        with local.cwd(mozjs_obj_dir):
            runner(make["check-jstests"])
