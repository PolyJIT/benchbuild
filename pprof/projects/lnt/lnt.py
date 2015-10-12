#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import Project, ProjectFactory

from os import path
from plumbum import local


class LNTGroup(Project):

    """LNT ProjectGroup for running the lnt test suite."""

    def __init__(self, exp, name):
        super(LNTGroup, self).__init__(exp, name, "lnt", "lnt")

    src_dir = "lnt"
    src_uri = "http://llvm.org/git/lnt"
    test_suite_dir = "test-suite"
    test_suite_uri = "http://llvm.org/git/test-suite"

    def download(self):
        from pprof.utils.downloader import Git
        from plumbum.cmd import virtualenv
        with local.cwd(self.builddir):
            Git(self.src_uri, self.src_dir)
            Git(self.test_suite_uri, self.test_suite_dir)

            virtualenv("local")
            python = local[path.join("local", "bin", "python")]
            python(path.join(self.src_dir, "setup.py"), "develop")

    def configure(self):
        from plumbum.cmd import mkdir, rm
        sandbox_dir = path.join(self.builddir, "run")
        if path.exists(sandbox_dir):
            rm("-rf", sandbox_dir)

        mkdir(sandbox_dir)

    def build(self):
        pass


class SingleSourceBenchmarks(LNTGroup):

    class Factory:

        def create(self, exp):
            return SingleSourceBenchmarks(exp, "SingleSourceBenchmarks")
    ProjectFactory.addFactory("SingleSourceBenchmarks", Factory())

    def run_tests(self, experiment):
        from pprof.project import wrap_dynamic
        from pprof.utils.compiler import lt_clang, lt_clang_cxx
        from pprof.utils.run import run

        exp = wrap_dynamic("lnt_runner", experiment)
        lnt = local[path.join("local", "bin", "lnt")]
        sandbox_dir = path.join(self.builddir, "run")

        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                     self.compiler_extension)

        run(lnt["runtest", "nt", "-v", "-j1", "--sandbox", sandbox_dir,
                "--cc", str(clang),
                "--cxx", str(clang_cxx),
                "--test-suite", path.join(self.builddir, self.test_suite_dir),
                "--test-style", "simple",
                "--make-param=RUNUNDER=" + str(exp),
                "--only-test=" + path.join("SingleSource", "Benchmarks"), "-v"])


class MultiSourceBenchmarks(LNTGroup):

    class Factory:

        def create(self, exp):
            return MultiSourceBenchmarks(exp, "MultiSourceBenchmarks")
    ProjectFactory.addFactory("MultiSourceBenchmarks", Factory())

    def run_tests(self, experiment):
        from pprof.project import wrap_dynamic
        from pprof.utils.compiler import lt_clang, lt_clang_cxx
        from pprof.utils.run import run

        exp = wrap_dynamic("lnt_runner", experiment)
        lnt = local[path.join("local", "bin", "lnt")]
        sandbox_dir = path.join(self.builddir, "run")

        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                     self.compiler_extension)

        run(lnt["runtest", "nt", "-v", "-j1", "--sandbox", sandbox_dir,
                "--cc", str(clang),
                "--cxx", str(clang_cxx),
                "--test-suite", path.join(self.builddir, self.test_suite_dir),
                "--test-style", "simple",
                "--make-param=RUNUNDER=" + str(exp),
                "--only-test=" + path.join("MultiSource", "Benchmarks")])


class MultiSourceApplications(LNTGroup):

    class Factory:

        def create(self, exp):
            return MultiSourceApplications(exp, "MultiSourceApplications")
    ProjectFactory.addFactory("MultiSourceApplications", Factory())

    def run_tests(self, experiment):
        from pprof.project import wrap_dynamic
        from pprof.utils.compiler import lt_clang, lt_clang_cxx
        from pprof.utils.run import run

        exp = wrap_dynamic("lnt_runner", experiment)
        lnt = local[path.join("local", "bin", "lnt")]
        sandbox_dir = path.join(self.builddir, "run")

        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                     self.compiler_extension)

        run(lnt["runtest", "nt", "-v", "-j1", "--sandbox", sandbox_dir,
                "--cc", str(clang),
                "--cxx", str(clang_cxx),
                "--test-suite", path.join(self.builddir, self.test_suite_dir),
                "--test-style", "simple",
                "--make-param=RUNUNDER=" + str(exp),
                "--only-test=" + path.join("MultiSource", "Applications")])


class SPEC2006(LNTGroup):

    class Factory:

        def create(self, exp):
            return SPEC2006(exp, "SPEC2006")
    ProjectFactory.addFactory("SPEC2006", Factory())

    def download(self):
        from pprof.utils.downloader import CopyNoFail
        from pprof.settings import config

        with local.cwd(self.builddir):
            if CopyNoFail('speccpu2006'):
                super(SPEC2006, self).download()
            else:
                print('======================================================')
                print('SPECCPU2006 not found in %s. This project will fail.',
                      config['tmpdir'])
                print('======================================================')

    def run_tests(self, experiment):
        from pprof.project import wrap_dynamic
        from pprof.utils.compiler import lt_clang, lt_clang_cxx
        from pprof.utils.run import run

        exp = wrap_dynamic("lnt_runner", experiment)
        lnt = local[path.join("local", "bin", "lnt")]
        sandbox_dir = path.join(self.builddir, "run")

        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                     self.compiler_extension)

        run(lnt["runtest", "nt", "-v", "-j1", "--sandbox", sandbox_dir,
                "--cc", str(clang),
                "--cxx", str(clang_cxx),
                "--test-suite", path.join(self.builddir, self.test_suite_dir),
                "--test-style", "simple",
                "--test-external", self.builddir,
                "--make-param=RUNUNDER=" + str(exp),
                "--only-test=" + path.join("External", "SPEC")])
