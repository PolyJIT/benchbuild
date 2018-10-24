from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, download, wrapping
from benchbuild.utils.cmd import cat, make, unzip


@download.with_wget({
    "2.1.4":
    "http://crocopat.googlecode.com/files/crocopat-2.1.4.zip"
})
class Crocopat(project.Project):
    """ crocopat benchmark """

    NAME = 'crocopat'
    DOMAIN = 'verification'
    GROUP = 'benchbuild'
    VERSION = '2.1.4'
    SRC_FILE = "crocopat.zip"

    def run_tests(self, runner):
        crocopat = wrapping.wrap(self.run_f, self)

        programs = local.path(self.testdir) / "programs" // "*.rml"
        projects = local.path(self.testdir) / "projects" // "*.rsf"
        for program in programs:
            for _project in projects:
                runner((cat[_project] | crocopat[program]), None)

    def compile(self):
        self.download()
        unzip(self.src_file)
        unpack_dir = "crocopat-{0}".format(self.version)

        crocopat_dir = local.path(unpack_dir) / "src"
        self.cflags += ["-I.", "-ansi"]
        self.ldflags += ["-L.", "-lrelbdd"]
        clang_cxx = compiler.cxx(self)

        with local.cwd(crocopat_dir):
            make("CXX=" + str(clang_cxx))
