from plumbum import local

from benchbuild.environments import container
from benchbuild.project import Project
from benchbuild.source import HTTP
from benchbuild.utils.cmd import cat, make, unzip, tar


class Crocopat(Project):
    """ crocopat benchmark """

    NAME: str = 'crocopat'
    DOMAIN: str = 'verification'
    GROUP: str = 'benchbuild'
    SOURCE = [
        HTTP(remote={
            '2.1.4': 'http://crocopat.googlecode.com/files/crocopat-2.1.4.zip'
        },
             local='crocopat.zip'),
        HTTP(remote={
            '2014-10': 'http://lairosiel.de/dist/2014-10-crocopat.tar.gz'
        },
             local='inputs.tar.gz')
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def run_tests(self):
        crocopat = wrapping.wrap('crocopat', self)
        test_source = self.source_of('inputs.tar.gz')
        tar('xf', test_source)

        test_dir = local.path('./crocopat/')
        programs = test_dir / "programs" // "*.rml"
        projects = test_dir / "projects" // "*.rsf"
        for program in programs:
            for _project in projects:
                crocopat_project = run.watch(
                    (cat[_project] | crocopat[program]))
                crocopat_project(retcode=None)

    def compile(self):
        crocopat_source = local.path(self.source_of('crocopat.zip'))
        crocopat_version = self.version_of('crocopat.zip')
        unzip(crocopat_source)
        unpack_dir = f'crocopat-{crocopat_version}'

        crocopat_dir = local.path(unpack_dir) / "src"
        self.cflags += ["-I.", "-ansi"]
        self.ldflags += ["-L.", "-lrelbdd"]
        clang_cxx = compiler.cxx(self)

        with local.cwd(crocopat_dir):
            make_ = run.watch(make)
            make_("CXX=" + str(clang_cxx))
