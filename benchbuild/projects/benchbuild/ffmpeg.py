from plumbum import local

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import Rsync, Wget, with_wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_wget({"3.1.3": "http://ffmpeg.org/releases/ffmpeg-3.1.3.tar.bz2"})
class LibAV(Project):
    """ LibAV benchmark """
    NAME = 'ffmpeg'
    DOMAIN = 'multimedia'
    GROUP = 'benchbuild'
    VERSION = '3.1.3'
    SRC_FILE = "ffmpeg.tar.bz2"

    fate_dir = "fate-samples"
    fate_uri = "rsync://fate-suite.libav.org/fate-suite/"

    def run_tests(self, runner):
        unpack_dir = "ffmpeg-{0}".format(self.version)
        with local.cwd(unpack_dir):
            wrap(self.name, self)
            run(make["V=1", "-i", "fate"])

    def compile(self):
        self.download()
        tar('xfj', self.src_file)
        unpack_dir = "ffmpeg-{0}".format(self.version)
        clang = cc(self)

        with local.cwd(unpack_dir):
            Rsync(self.fate_uri, self.fate_dir)
            configure = local["./configure"]
            run(configure[
                "--disable-shared", "--cc=" + str(clang), "--extra-ldflags=" +
                " ".join(self.ldflags), "--samples=" + self.fate_dir])
            run(make["clean"])
            run(make["-j{0}".format(str(CFG["jobs"])), "all"])
