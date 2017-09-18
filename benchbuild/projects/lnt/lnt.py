"""
LNT based measurements.

"""
from os import path

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Git, CopyNoFail
from benchbuild.utils.wrapping import wrap_dynamic
from benchbuild.utils.cmd import virtualenv, mkdir, rm

from plumbum import local


class LNTGroup(Project):
    """LNT ProjectGroup for running the lnt test suite."""

    DOMAIN = 'lnt'
    GROUP = 'lnt'
    VERSION = '9.0.1.13'

    def __init__(self, exp):
        super(LNTGroup, self).__init__(exp, "lnt")

    src_dir = "lnt"
    src_uri = "http://llvm.org/git/lnt"
    test_suite_dir = "test-suite"
    test_suite_uri = "http://llvm.org/git/test-suite"

    def download(self):
        Git(self.src_uri, self.src_dir)
        Git(self.test_suite_uri, self.test_suite_dir)

        virtualenv("local", "--python=python2", )
        python = local[path.join("local", "bin", "python")]
        python(path.join(self.src_dir, "setup.py"), "develop")

    def configure(self):
        sandbox_dir = path.join(self.builddir, "run")
        if path.exists(sandbox_dir):
            rm("-rf", sandbox_dir)

        mkdir(sandbox_dir)

    def build(self):
        pass


class SingleSourceBenchmarks(LNTGroup):
    NAME = 'SingleSourceBenchmarks'

    def run_tests(self, experiment, run):
        exp = wrap_dynamic(self, "lnt_runner", experiment)
        lnt = local[path.join("local", "bin", "lnt")]
        sandbox_dir = path.join(self.builddir, "run")

        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        run(lnt["runtest", "nt", "-v", "-j1", "--sandbox", sandbox_dir, "--cc",
                str(clang), "--cxx", str(clang_cxx), "--test-suite", path.join(
                    self.builddir, self.test_suite_dir), "--test-style",
                "simple", "--make-param=RUNUNDER=" + str(exp), "--only-test=" +
                path.join("SingleSource", "Benchmarks"), "-v"])


class MultiSourceBenchmarks(LNTGroup):
    NAME = 'MultiSourceBenchmarks'

    def run_tests(self, experiment, run):
        exp = wrap_dynamic(self, "lnt_runner", experiment)
        lnt = local[path.join("local", "bin", "lnt")]
        sandbox_dir = path.join(self.builddir, "run")

        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        run(lnt["runtest", "nt", "-v", "-j1", "--sandbox", sandbox_dir, "--cc",
                str(clang), "--cxx", str(clang_cxx), "--test-suite", path.join(
                    self.builddir, self.test_suite_dir), "--test-style",
                "simple", "--make-param=RUNUNDER=" + str(exp), "--only-test=" +
                path.join("MultiSource", "Benchmarks")])


class MultiSourceApplications(LNTGroup):
    NAME = 'MultiSourceApplications'

    def run_tests(self, experiment, run):
        exp = wrap_dynamic(self, "lnt_runner", experiment)
        lnt = local[path.join("local", "bin", "lnt")]
        sandbox_dir = path.join(self.builddir, "run")

        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        run(lnt["runtest", "nt", "-v", "-j1", "--sandbox", sandbox_dir, "--cc",
                str(clang), "--cxx", str(clang_cxx), "--test-suite", path.join(
                    self.builddir, self.test_suite_dir), "--test-style",
                "simple", "--make-param=RUNUNDER=" + str(exp), "--only-test=" +
                path.join("MultiSource", "Applications")])


class SPEC2006(LNTGroup):
    NAME = 'SPEC2006'

    def download(self):
        if CopyNoFail('speccpu2006'):
            super(SPEC2006, self).download()
        else:
            print('======================================================')
            print(('SPECCPU2006 not found in %s. This project will fail.', CFG[
                'tmp_dir']))
            print('======================================================')

    def run_tests(self, experiment, run):
        exp = wrap_dynamic(self, "lnt_runner", experiment)
        lnt = local[path.join("local", "bin", "lnt")]
        sandbox_dir = path.join(self.builddir, "run")

        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        run(lnt["runtest", "nt", "-v", "-j1", "--sandbox", sandbox_dir, "--cc",
                str(clang), "--cxx", str(clang_cxx), "--test-suite", path.join(
                    self.builddir, self.test_suite_dir), "--test-style",
                "simple", "--test-externals", self.builddir,
                "--make-param=RUNUNDER=" + str(
                    exp), "--only-test=" + path.join("External", "SPEC")])


class Povray(LNTGroup):
    NAME = 'Povray'

    povray_url = "https://github.com/POV-Ray/povray"
    povray_src_dir = "Povray"

    def download(self):
        super(Povray, self).download()
        Git(self.povray_url, self.povray_src_dir)

    def run_tests(self, experiment, run):
        exp = wrap_dynamic(self, "lnt_runner", experiment)
        lnt = local[path.join("local", "bin", "lnt")]
        sandbox_dir = path.join(self.builddir, "run")

        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        run(lnt["runtest", "nt", "-v", "-j1", "--sandbox", sandbox_dir, "--cc",
                str(clang), "--cxx", str(clang_cxx), "--test-suite", path.join(
                    self.builddir, self.test_suite_dir), "--test-style",
                "simple", "--test-externals", self.builddir,
                "--make-param=RUNUNDER=" + str(
                    exp), "--only-test=" + path.join("External", "Povray")])
