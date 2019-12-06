from plumbum import local

import benchbuild as bb

from benchbuild.downloads import HTTP
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make, tar


class LibAV(bb.Project):
    """ LibAV benchmark """
    NAME: str = 'ffmpeg'
    DOMAIN: str = 'multimedia'
    GROUP: str = 'benchbuild'
    SOURCE = [
        HTTP(remote={
            '3.1.3': 'http://ffmpeg.org/releases/ffmpeg-3.1.3.tar.bz2'
        },
             local='ffmpeg.tar.bz2')
    ]

    fate_dir = "fate-samples"
    fate_uri = "rsync://fate-suite.libav.org/fate-suite/"

    def run_tests(self):
        ffmpeg_version = self.version_of('ffmpeg.tar.bz2')
        unpack_dir = bb.path(f'ffmpeg-{ffmpeg_version}')

        with bb.cwd(unpack_dir):
            bb.wrap(self.name, self)
            make_ = bb.watch(make)
            make_("V=1", "-i", "fate")

    def compile(self):
        ffmpeg_source = bb.path(self.source_of('ffmpeg.tar.bz2'))
        ffmpeg_version = self.version_of('ffmpeg.tar.bz2')
        tar('xfj', ffmpeg_source)
        unpack_dir = bb.path(f'ffmpeg-{ffmpeg_version}')
        clang = bb.compiler.cc(self)

        with local.cwd(unpack_dir):
            bb.download.Rsync(self.fate_uri, self.fate_dir)
            configure = local["./configure"]
            configure = bb.watch(configure)
            make_ = bb.watch(make)

            configure("--disable-shared", "--cc=" + str(clang),
                      "--extra-ldflags=" + " ".join(self.ldflags),
                      "--samples=" + self.fate_dir)
            make_("clean")
            make_("-j{0}".format(str(CFG["jobs"])), "all")
