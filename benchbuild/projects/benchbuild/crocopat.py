from plumbum import local

import benchbuild as bb

from benchbuild.source import HTTP
from benchbuild.utils.cmd import cat, make, unzip, tar


class Crocopat(bb.Project):
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
        }, local='inputs.tar.gz')
    ]

    def run_tests(self):
        crocopat = bb.wrap('crocopat', self)
        test_source = self.source_of('inputs.tar.gz')
        tar('xf', test_source)

        test_dir = local.path('./crocopat/')
        programs = test_dir / "programs" // "*.rml"
        projects = test_dir / "projects" // "*.rsf"
        for program in programs:
            for _project in projects:
                crocopat_project = bb.watch(
                    (cat[_project] | crocopat[program]))
                crocopat_project(retcode=None)

    def compile(self):
        crocopat_source = bb.path(self.source_of('crocopat.zip'))
        crocopat_version = self.version_of('crocopat.zip')
        unzip(crocopat_source)
        unpack_dir = f'crocopat-{crocopat_version}'

        crocopat_dir = bb.path(unpack_dir) / "src"
        self.cflags += ["-I.", "-ansi"]
        self.ldflags += ["-L.", "-lrelbdd"]
        clang_cxx = bb.compiler.cxx(self)

        with bb.cwd(crocopat_dir):
            make_ = bb.watch(make)
            make_("CXX=" + str(clang_cxx))
