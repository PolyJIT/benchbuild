from plumbum import local

from benchbuild import project
from benchbuild.downloads import HTTP
from benchbuild.settings import CFG
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make, tar


class LibAV(project.Project):
    """ LibAV benchmark """
    NAME = 'ffmpeg'
    DOMAIN = 'multimedia'
    GROUP = 'benchbuild'
    VERSION = '3.1.3'
    SOURCE = [
        HTTP(remote={
            '3.1.3': 'http://ffmpeg.org/releases/ffmpeg-3.1.3.tar.bz2'
        },
             local='ffmpeg.tar.bz2')
    ]

    fate_dir = "fate-samples"
    fate_uri = "rsync://fate-suite.libav.org/fate-suite/"

    def run_tests(self):
        unpack_dir = "ffmpeg-{0}".format(self.version)
        with local.cwd(unpack_dir):
            wrapping.wrap(self.name, self)
            make_ = run.watch(make)
            make_("V=1", "-i", "fate")

    def compile(self):
        ffmpeg_source = local.path(self.source[0].local)
        tar('xfj', ffmpeg_source)
        unpack_dir = "ffmpeg-{0}".format(self.version)
        clang = compiler.cc(self)

        with local.cwd(unpack_dir):
            download.Rsync(self.fate_uri, self.fate_dir)
            configure = local["./configure"]
            configure = run.watch(configure)
            make_ = run.watch(make)

            configure("--disable-shared", "--cc=" + str(clang),
                      "--extra-ldflags=" + " ".join(self.ldflags),
                      "--samples=" + self.fate_dir)
            make_("clean")
            make_("-j{0}".format(str(CFG["jobs"])), "all")
