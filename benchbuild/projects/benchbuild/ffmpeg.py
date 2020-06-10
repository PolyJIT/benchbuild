from plumbum import local

from benchbuild import project
from benchbuild.settings import CFG
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.settings import get_number_of_jobs


@download.with_wget(
    {"3.1.3": "http://ffmpeg.org/releases/ffmpeg-3.1.3.tar.bz2"})
class LibAV(project.Project):
    """ LibAV benchmark """
    NAME = 'ffmpeg'
    DOMAIN = 'multimedia'
    GROUP = 'benchbuild'
    VERSION = '3.1.3'
    SRC_FILE = "ffmpeg.tar.bz2"

    fate_dir = "fate-samples"
    fate_uri = "rsync://fate-suite.libav.org/fate-suite/"

    def run_tests(self):
        unpack_dir = "ffmpeg-{0}".format(self.version)
        with local.cwd(unpack_dir):
            wrapping.wrap(self.name, self)
            _make = run.watch(make)
            _make("V=1", "-i", "fate")

    def compile(self):
        self.download()
        tar('xfj', self.src_file)
        unpack_dir = "ffmpeg-{0}".format(self.version)
        clang = compiler.cc(self)

        with local.cwd(unpack_dir):
            download.Rsync(self.fate_uri, self.fate_dir)
            configure = local["./configure"]
            _configure = run.watch(configure)
            _make = run.watch(make)

            _configure("--disable-shared", "--cc=" + str(clang),
                       "--extra-ldflags=" + " ".join(self.ldflags),
                       "--samples=" + self.fate_dir)
            _make("clean")
            _make("-j{0}".format(str(get_number_of_jobs(CFG))), "all")
