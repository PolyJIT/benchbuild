"""LNT based measurements."""
import logging
from os import path

from plumbum import FG, local

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import cat, mkdir, rm, virtualenv
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import CopyNoFail, with_git, Git
from benchbuild.utils.wrapping import wrap_dynamic

LOG = logging.getLogger(__name__)


@with_git("http://llvm.org/git/lnt", limit=5)
class LNTGroup(Project):
    """LNT ProjectGroup for running the lnt test suite."""

    DOMAIN = 'lnt'
    GROUP = 'lnt'
    VERSION = 'HEAD'
    NAME_FILTERS = [
        r'(?P<name>.+)\.simple',
        r'(?P<name>.+)-(dbl|flt)',
    ]
    SUBDIR = None
    SRC_FILE = "lnt.git"

    src_dir = "lnt"
    test_suite_dir = "test-suite"
    test_suite_uri = "http://llvm.org/git/test-suite"

    # Will be set by configure.
    lnt = None
    sandbox_dir = None
    clang = None
    clang_cxx = None
    binary = None

    def compile(self):
        self.download()
        Git(self.test_suite_uri, self.test_suite_dir)

        venv_path = local.cwd / "local"
        virtualenv(venv_path, "--python=python2")
        pip_path = local.cwd / "local" / "bin" / "pip"
        pip = local[pip_path]
        with local.cwd(self.SRC_FILE):
            pip("install", "--no-cache-dir", "--disable-pip-version-check",
                "-e", ".")

        self.sandbox_dir = local.cwd / "run"
        if self.sandbox_dir.exists():
            rm("-rf", self.sandbox_dir)
        mkdir(self.sandbox_dir)

        self.lnt = local[local.path("./local/bin/lnt")]
        self.clang = cc(self, detect_project=True)
        self.clang_cxx = cxx(self, detect_project=True)

        self.lnt("runtest", "test-suite", "-v", "-j1", "--sandbox",
                 self.sandbox_dir, "--benchmarking-only",
                 "--only-compile", "--cc", str(self.clang), "--cxx",
                 str(self.clang_cxx), "--test-suite", self.test_suite_dir,
                 "--only-test=" + self.SUBDIR)

    @staticmethod
    def after_run_tests(sandbox_dir):
        logfiles = local.path(sandbox_dir) // "*" / "test.log"
        for log in logfiles:
            LOG.info("Dumping contents of: %s", log)
            (cat[log] & FG)  # pylint: disable=pointless-statement

    def run_tests(self, runner):
        binary = wrap_dynamic(
            self, "lnt_runner", name_filters=LNTGroup.NAME_FILTERS)

        runner(
            self.lnt["runtest", "nt", "-v", "-j1", "--sandbox",
                     self.sandbox_dir, "--benchmarking-only", "--cc",
                     str(self.clang), "--cxx",
                     str(self.clang_cxx), "--test-suite", self.test_suite_dir,
                     "--test-style", "simple", "--test-externals",
                     self.builddir, "--make-param=RUNUNDER=" +
                     str(binary), "--only-test=" + self.SUBDIR])

        LNTGroup.after_run_tests(self.sandbox_dir)


class SingleSourceBenchmarks(LNTGroup):
    NAME = 'SingleSourceBenchmarks'
    DOMAIN = 'LNT (SSB)'
    SUBDIR = path.join("SingleSource", "Benchmarks")


class MultiSourceBenchmarks(LNTGroup):
    NAME = 'MultiSourceBenchmarks'
    DOMAIN = 'LNT (MSB)'
    SUBDIR = path.join("MultiSource", "Benchmarks")


class MultiSourceApplications(LNTGroup):
    NAME = 'MultiSourceApplications'
    DOMAIN = 'LNT (MSA)'
    SUBDIR = path.join("MultiSource", "Applications")


class SPEC2006(LNTGroup):
    NAME = 'SPEC2006'
    DOMAIN = 'LNT (Ext)'
    SUBDIR = path.join("External", "SPEC")

    def compile(self):
        if CopyNoFail('speccpu2006'):
            super(SPEC2006, self).compile()
        else:
            print('======================================================')
            print(('SPECCPU2006 not found in %s. This project will fail.',
                   CFG['tmp_dir']))
            print('======================================================')


class Povray(LNTGroup):
    NAME = 'Povray'
    DOMAIN = 'LNT (Ext)'
    SUBDIR = path.join("External", "Povray")

    povray_url = "https://github.com/POV-Ray/povray"
    povray_src_dir = "Povray"

    def compile(self):
        Git(self.povray_url, self.povray_src_dir)
        super(Povray, self).compile()
