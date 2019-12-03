from plumbum import local

from benchbuild import project
from benchbuild.downloads import HTTP
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import cat, make, unzip


class Crocopat(project.Project):
    """ crocopat benchmark """

    NAME = 'crocopat'
    DOMAIN = 'verification'
    GROUP = 'benchbuild'
    VERSION = '2.1.4'
    SOURCE = [
        HTTP(remote={
            '2.1.4': 'http://crocopat.googlecode.com/files/crocopat-2.1.4.zip'
        },
             local='crocopat.zip')
    ]

    def run_tests(self):
        crocopat = wrapping.wrap('crocopat', self)

        programs = local.path(self.testdir) / "programs" // "*.rml"
        projects = local.path(self.testdir) / "projects" // "*.rsf"
        for program in programs:
            for _project in projects:
                crocopat_project = run.watch(
                    (cat[_project] | crocopat[program]))
                crocopat_project(retcode=None)

    def compile(self):
        crocopat_source = local.path(self.source[0].local)
        unzip(crocopat_source)
        unpack_dir = "crocopat-{0}".format(self.version)

        crocopat_dir = local.path(unpack_dir) / "src"
        self.cflags += ["-I.", "-ansi"]
        self.ldflags += ["-L.", "-lrelbdd"]
        clang_cxx = compiler.cxx(self)

        with local.cwd(crocopat_dir):
            make_ = run.watch(make)
            make_("CXX=" + str(clang_cxx))
