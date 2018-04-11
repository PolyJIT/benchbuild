"""LNT based measurements."""
import logging
from glob import glob
from os import path

from plumbum import FG, local

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import cat, mkdir, rm, virtualenv
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import CopyNoFail, Git
from benchbuild.utils.wrapping import wrap_dynamic

LOG = logging.getLogger(__name__)


class LNTGroup(Project):
    """LNT ProjectGroup for running the lnt test suite."""

    DOMAIN = 'lnt'
    GROUP = 'lnt'
    VERSION = '9.0.1.13'

    NAME_FILTERS = [
        r'(?P<name>.+)\.simple',
        r'(?P<name>.+)-(dbl|flt)',
    ]

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

    def before_run_tests(self, experiment):
        exp = wrap_dynamic(self, "lnt_runner", experiment,
                           name_filters=LNTGroup.NAME_FILTERS)
        lnt = local[path.join("local", "bin", "lnt")]
        sandbox_dir = path.join(self.builddir, "run")
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        return (exp, lnt, sandbox_dir, clang, clang_cxx)

    @staticmethod
    def after_run_tests(sandbox_dir):
        logfiles = glob(path.join(sandbox_dir, "./*/test.log"))
        for log in logfiles:
            LOG.info("Dumping contents of: %s", log)
            (cat[log] & FG) # pylint: disable=pointless-statement

    def build(self):
        pass


class SingleSourceBenchmarks(LNTGroup):
    NAME = 'SingleSourceBenchmarks'
    DOMAIN = 'LNT (SSB)'

    def run_tests(self, experiment, runner):
        exp, lnt, sandbox_dir, clang, clang_cxx = \
            self.before_run_tests(experiment)

        runner(lnt["runtest", "nt", "-v", "-j1",
                   "--sandbox", sandbox_dir,
                   "--cc", str(clang),
                   "--cxx", str(clang_cxx),
                   "--test-suite", path.join(self.builddir,
                                             self.test_suite_dir),
                   "--test-style", "simple",
                   "--make-param=RUNUNDER=" + str(exp),
                   "--only-test=" + path.join("SingleSource", "Benchmarks")])

        type(self).after_run_tests(sandbox_dir)


class MultiSourceBenchmarks(LNTGroup):
    NAME = 'MultiSourceBenchmarks'
    DOMAIN = 'LNT (MSB)'

    def run_tests(self, experiment, runner):
        exp, lnt, sandbox_dir, clang, clang_cxx = \
            self.before_run_tests(experiment)

        runner(lnt["runtest", "nt", "-v", "-j1",
                   "--sandbox", sandbox_dir,
                   "--cc", str(clang),
                   "--cxx", str(clang_cxx),
                   "--test-suite", path.join(self.builddir,
                                             self.test_suite_dir),
                   "--test-style", "simple",
                   "--make-param=RUNUNDER=" + str(exp),
                   "--only-test=" + path.join("MultiSource", "Benchmarks")])

        type(self).after_run_tests(sandbox_dir)


class MultiSourceApplications(LNTGroup):
    NAME = 'MultiSourceApplications'
    DOMAIN = 'LNT (MSA)'

    def run_tests(self, experiment, runner):
        exp, lnt, sandbox_dir, clang, clang_cxx = \
            self.before_run_tests(experiment)

        runner(lnt["runtest", "nt", "-v", "-j1",
                   "--sandbox", sandbox_dir,
                   "--cc", str(clang),
                   "--cxx", str(clang_cxx),
                   "--test-suite", path.join(self.builddir,
                                             self.test_suite_dir),
                   "--test-style", "simple",
                   "--make-param=RUNUNDER=" + str(exp),
                   "--only-test=" + path.join("MultiSource", "Applications")])

        type(self).after_run_tests(sandbox_dir)


class SPEC2006(LNTGroup):
    NAME = 'SPEC2006'
    DOMAIN = 'LNT (Ext)'

    def download(self):
        if CopyNoFail('speccpu2006'):
            super(SPEC2006, self).download()
        else:
            print('======================================================')
            print(('SPECCPU2006 not found in %s. This project will fail.',
                   CFG['tmp_dir']))
            print('======================================================')

    def run_tests(self, experiment, runner):
        exp, lnt, sandbox_dir, clang, clang_cxx = \
            self.before_run_tests(experiment)

        runner(lnt["runtest", "nt", "-v", "-j1",
                   "--sandbox", sandbox_dir,
                   "--cc", str(clang),
                   "--cxx", str(clang_cxx),
                   "--test-suite", path.join(self.builddir,
                                             self.test_suite_dir),
                   "--test-style", "simple",
                   "--test-externals", self.builddir,
                   "--make-param=RUNUNDER=" + str(exp),
                   "--only-test=" + path.join("External", "SPEC")])

        self.after_run_tests(sandbox_dir)


class Povray(LNTGroup):
    NAME = 'Povray'
    DOMAIN = 'LNT (Ext)'

    povray_url = "https://github.com/POV-Ray/povray"
    povray_src_dir = "Povray"

    def download(self):
        super(Povray, self).download()
        Git(self.povray_url, self.povray_src_dir)

    def run_tests(self, experiment, runner):
        exp, lnt, sandbox_dir, clang, clang_cxx = \
            self.before_run_tests(experiment)

        runner(lnt["runtest", "nt", "-v", "-j1",
                   "--sandbox", sandbox_dir,
                   "--cc", str(clang),
                   "--cxx", str(clang_cxx),
                   "--test-suite", path.join(self.builddir,
                                             self.test_suite_dir),
                   "--test-style", "simple",
                   "--test-externals", self.builddir,
                   "--make-param=RUNUNDER=" + str(exp),
                   "--only-test=" + path.join("External", "Povray")])

        self.after_run_tests(sandbox_dir)
