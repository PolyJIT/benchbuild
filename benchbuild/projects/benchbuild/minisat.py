from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import HTTP, Git
from benchbuild.utils.cmd import make, tar


class Minisat(bb.Project):
    """ minisat benchmark """

    NAME = 'minisat'
    DOMAIN = 'verification'
    GROUP = 'benchbuild'
    SOURCE = [
        Git(
            remote='https://github.com/niklasso/minisat',
            local='minisat.git',
            limit=5,
            refspec='HEAD'
        ),
        HTTP(
            remote={
                '2016-11-minisat.tar.gz':
                    'http://lairosiel.de/dist/2016-11-minisat.tar.gz'
            },
            local='inputs.tar.gz'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def run_tests(self):
        minisat_repo = local.path(self.source_of('minisat.git'))
        minisat_build = minisat_repo / 'build' / 'dynamic'
        minisat_lib = minisat_build / 'lib'
        minisat_bin = minisat_build / 'bin'

        test_source = local.path(self.source_of('inputs.tar.gz'))
        test_dir = local.path('./minisat/')
        tar('xf', test_source)

        testfiles = test_dir // "*.cnf.gz"

        minisat = bb.wrap(minisat_bin / "minisat", self)
        for test_f in testfiles:
            _minisat = bb.watch(
                (minisat.with_env(LD_LIBRARY_PATH=minisat_lib) < test_f)
            )
            _minisat()

    def compile(self):
        minisat_repo = local.path(self.source_of('minisat.git'))
        with local.cwd(minisat_repo):
            _make = bb.watch(make)
            _make("config")

            clang = bb.compiler.cc(self)
            clang_cxx = bb.compiler.cxx(self)

            _make(
                "CC=" + str(clang), "CXX=" + str(clang_cxx), "clean", "lsh",
                "sh"
            )
