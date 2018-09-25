from functools import partial
from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make, mkdir, tar
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import with_git
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_git(
    "https://github.com/mozilla/gecko-dev.git",
    target_dir="gecko-dev.git",
    clone=False,
    limit=5)
class SpiderMonkey(Project):
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

        js_dir = path.join(self.src_file, "js", "src")
        clang = cc(self)
        clang_cxx = cxx(self)
        with local.cwd(js_dir):
            make_src_pkg = local["./make-source-package.sh"]
            with local.env(
                    DIST=self.builddir,
                    MOZJS_MAJOR_VERSION=0,
                    MOZJS_MINOR_VERSION=0,
                    MOZJS_PATCH_VERSION=0):
                make_src_pkg()

        mozjs_dir = "mozjs-0.0.0"
        tar("xfj", mozjs_dir + ".tar.bz2")
        with local.cwd(path.join(mozjs_dir, "js", "src")):
            mkdir("obj")
            autoconf = local["autoconf-2.13"]
            autoconf()
            with local.cwd("obj"):
                with local.env(CC=str(clang), CXX=str(clang_cxx)):
                    configure = local["../configure"]
                    configure = configure["--without-system-zlib"]
                    run(configure)

        mozjs_dir = path.join("mozjs-0.0.0", "js", "src", "obj")
        with local.cwd(mozjs_dir):
            run(make["-j", CFG["jobs"].value()])

    def run_tests(self, runner):
        mozjs_dir = path.join("mozjs-0.0.0", "js", "src", "obj")
        self.runtime_extension = partial(self, may_wrap=False)
        wrap(path.join(mozjs_dir, "js", "src", "shell", "js"), self)

        with local.cwd(mozjs_dir):
            run(make["check-jstests"])
