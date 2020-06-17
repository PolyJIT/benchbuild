import benchbuild as bb
from benchbuild.utils import download
from benchbuild.utils.cmd import cat, make, unzip


@download.with_wget(
    {"2.1.4": "http://crocopat.googlecode.com/files/crocopat-2.1.4.zip"})
class Crocopat(bb.Project):
    """ crocopat benchmark """

    NAME = 'crocopat'
    DOMAIN = 'verification'
    GROUP = 'benchbuild'
    VERSION = '2.1.4'
    SRC_FILE = "crocopat.zip"

    def run_tests(self):
        crocopat = bb.wrap('crocopat', self)

        programs = bb.path(self.testdir) / "programs" // "*.rml"
        projects = bb.path(self.testdir) / "projects" // "*.rsf"
        for program in programs:
            for _project in projects:
                _crocopat_project = bb.watch(
                    (cat[_project] | crocopat[program]))
                _crocopat_project(retcode=None)

    def compile(self):
        self.download()
        unzip(self.src_file)
        unpack_dir = "crocopat-{0}".format(self.version)

        crocopat_dir = bb.path(unpack_dir) / "src"
        self.cflags += ["-I.", "-ansi"]
        self.ldflags += ["-L.", "-lrelbdd"]
        clang_cxx = bb.compiler.cxx(self)

        with bb.cwd(crocopat_dir):
            _make = bb.watch(make)
            _make("CXX=" + str(clang_cxx))
