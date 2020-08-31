"""LNT based measurements."""
import logging

from plumbum import FG, local

import benchbuild as bb
from benchbuild.settings import CFG
from benchbuild.source import Git
from benchbuild.utils.cmd import cat, mkdir, rm, virtualenv

LOG = logging.getLogger(__name__)


class LNTGroup(bb.Project):
    """LNT ProjectGroup for running the lnt test suite."""

    DOMAIN = 'lnt'
    GROUP = 'lnt'
    NAME_FILTERS = [
        r'(?P<name>.+)\.simple',
        r'(?P<name>.+)-(dbl|flt)',
    ]
    SUBDIR = None
    SOURCE = [
        Git(remote='http://llvm.org/git/lnt',
            local='lnt.git',
            refspec='HEAD',
            limit=5),
        Git(remote='http://llvm.org/git/test-suite',
            local='test-suite',
            refspec='HEAD',
            limit=5)
    ]

    # Will be set by configure.
    lnt = None
    sandbox_dir = None
    clang = None
    clang_cxx = None
    binary = None

    def compile(self):
        lnt_repo = local.path(self.source_of('lnt.git'))
        test_suite_source = local.path(self.source_of('test-suite'))

        venv_path = local.cwd / "local"
        virtualenv(venv_path, "--python=python2")
        pip_path = local.cwd / "local" / "bin" / "pip"
        pip = local[pip_path]

        with local.cwd(lnt_repo):
            pip("install", "--no-cache-dir", "--disable-pip-version-check",
                "-e", ".")

        self.sandbox_dir = local.cwd / "run"
        if self.sandbox_dir.exists():
            rm("-rf", self.sandbox_dir)
        mkdir(self.sandbox_dir)

        self.lnt = local[local.path("./local/bin/lnt")]
        self.clang = bb.compiler.cc(self, detect_project=True)
        self.clang_cxx = bb.compiler.cxx(self, detect_project=True)

        _runtest = bb.watch(self.lnt)
        _runtest("runtest", "test-suite", "-v", "-j1", "--sandbox",
                 self.sandbox_dir, "--benchmarking-only",
                 "--only-compile", "--cc", str(self.clang), "--cxx",
                 str(self.clang_cxx), "--test-suite", test_suite_source,
                 "--only-test=" + self.SUBDIR)

    @staticmethod
    def after_run_tests(sandbox_dir):
        logfiles = local.path(sandbox_dir) // "*" / "test.log"
        for log in logfiles:
            LOG.info("Dumping contents of: %s", log)
            (cat[log] & FG)  # pylint: disable=pointless-statement

    def run_tests(self):
        test_suite_source = local.path(self.source_of('test-suite'))
        binary = bb.wrapping.wrap_dynamic(self,
                                          "lnt_runner",
                                          name_filters=LNTGroup.NAME_FILTERS)

        _runtest = bb.watch(self.lnt)
        _runtest("runtest", "nt", "-v", "-j1", "--sandbox", self.sandbox_dir,
                 "--benchmarking-only", "--cc", str(self.clang), "--cxx",
                 str(self.clang_cxx), "--test-suite", test_suite_source,
                 "--test-style", "simple", "--test-externals", self.builddir,
                 "--make-param=RUNUNDER=" + str(binary),
                 "--only-test=" + self.SUBDIR)

        LNTGroup.after_run_tests(self.sandbox_dir)


class SingleSourceBenchmarks(LNTGroup):
    NAME = 'SingleSourceBenchmarks'
    DOMAIN = 'LNT (SSB)'
    SUBDIR = "SingleSource/Benchmarks"


class MultiSourceBenchmarks(LNTGroup):
    NAME = 'MultiSourceBenchmarks'
    DOMAIN = 'LNT (MSB)'
    SUBDIR = "MultiSource/Benchmarks"


class MultiSourceApplications(LNTGroup):
    NAME = 'MultiSourceApplications'
    DOMAIN = 'LNT (MSA)'
    SUBDIR = "MultiSource/Applications"


class SPEC2006(LNTGroup):
    NAME = 'SPEC2006'
    DOMAIN = 'LNT (Ext)'
    SUBDIR = "External/SPEC"

    def compile(self):
        if bb.download.CopyNoFail('speccpu2006'):
            super(SPEC2006, self).compile()
        else:
            print('======================================================')
            print(('SPECCPU2006 not found in %s. This project will fail.',
                   CFG['tmp_dir']))
            print('======================================================')


class Povray(LNTGroup):
    NAME = 'Povray'
    DOMAIN = 'LNT (Ext)'
    SUBDIR = "External/Povray"
    SOURCE = [
        Git(remote='http://llvm.org/git/lnt',
            local='lnt.git',
            refspec='HEAD',
            limit=5),
        Git(remote='http://llvm.org/git/test-suite',
            local='test-suite',
            refspec='HEAD',
            limit=5),
        Git(remote='https://github.com/POV-Ray/povray',
            local='povray.git',
            refspec='HEAD',
            limit=5)
    ]
