from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.project import wrap
from benchbuild.settings import CFG
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Git
from benchbuild.utils.run import run

from plumbum import local
from benchbuild.utils.cmd import make, mkdir

from os import path


class SpiderMonkey(BenchBuildGroup):
    NAME = 'js'
    DOMAIN = 'compilation'

    src_uri = "https://github.com/mozilla/gecko-dev.git"
    src_dir = "gecko-dev.git"

    def download(self):
        Git(self.src_uri, self.src_dir)

    def configure(self):
        js_dir = path.join(self.src_dir, "js", "src")
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)
        with local.cwd(js_dir):
            autoconf = local["autoconf"]
            autoconf()
            mkdir("build_OPT.OBJ")
            with local.cwd("build_OPT.OBJ"):
                with local.env(CC=str(clang), CXX=str(clang_cxx)):
                    configure = local["../configure"]
                    run(configure)

    def build(self):
        js_dir = path.join(self.src_dir, "js", "src", "build_OPT.OBJ")
        with local.cwd(js_dir):
            run(make["-j", CFG["available_cpu_count"].value()])

    def run_tests(self, experiment):
        js_dir = path.join(self.src_dir, "js", "src")
        js_build_dir = path.join(js_dir, "build_OPT.OBJ")
        wrap(path.join(js_build_dir, "bin", "js"), experiment)

        with local.cwd(js_build_dir):
            run(make["check"])
