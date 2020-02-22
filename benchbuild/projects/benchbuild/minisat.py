from benchbuild.project import Project
from benchbuild.environments import container
from benchbuild.source import Git, HTTP
from benchbuild.utils.cmd import git, make, tar


class Minisat(Project):
    """ minisat benchmark """

    NAME: str = 'minisat'
    DOMAIN: str = 'verification'
    GROUP: str = 'benchbuild'
    SOURCE = [
        Git(remote='https://github.com/niklasso/minisat',
            local='minisat.git',
            limit=5,
            refspec='HEAD'),
        HTTP(remote={
            '2016-11-minisat.tar.gz':
            'http://lairosiel.de/dist/2016-11-minisat.tar.gz'
        },
             local='inputs.tar.gz')
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def run_tests(self):
        minisat_repo = local.path(self.source_of('minisat.git'))
        minisat_build = minisat_repo / 'build' / 'dynamic'
        minisat_lib = minisat_build / 'lib'
        minisat_bin = minisat_build / 'bin'

        test_source = local.path(self.source_of('inputs.tar.gz'))
        test_dir = local.path('./minisat/')
        tar('xf', test_source)

        testfiles = test_dir // "*.cnf.gz"

        minisat = wrapping.wrap(minisat_bin / "minisat", self)
        for test_f in testfiles:
            minisat_test = run.watch(
                (minisat.with_env(LD_LIBRARY_PATH=minisat_lib) < test_f))
            minisat_test()

    def compile(self):
        minisat_repo = local.path(self.source_of('minisat.git'))
        with local.cwd(minisat_repo):
            # FIXME: That needs to be modeled with Git() download handlers.
            git("fetch", "origin", "pull/17/head:clang")
            git("checkout", "clang")
            #

            make_ = run.watch(make)
            make_("config")

            clang = compiler.cc(self)
            clang_cxx = compiler.cxx(self)

            make_("CC=" + str(clang), "CXX=" + str(clang_cxx), "clean", "lsh",
                  "sh")
