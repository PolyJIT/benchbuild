#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory
from pprof.settings import config
from pprof.projects.pprof.group import PprofGroup

from os import path

from plumbum import local
from plumbum.cmd import make


class LibAV(PprofGroup):
    """ LibAV benchmark """

    class Factory:
        def create(self, exp):
            return LibAV(exp, "ffmpeg", "multimedia")

    ProjectFactory.addFactory("LibAV", Factory())

    src_dir = "ffmpeg-2.6.3"
    src_file = src_dir + ".tar.bz2"
    src_uri = "http://ffmpeg.org/releases/" + src_file
    fate_dir = "fate-samples"
    fate_uri = "rsync://fate-suite.libav.org/fate-suite/"

    def run_tests(self, experiment):
        from pprof.project import wrap
        from pprof.utils.run import run

        libav_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(libav_dir):
            wrap(self.name, experiment)

        with local.cwd(self.src_dir):
            run(make["V=1", "-i", "fate"])

    def download(self):
        from pprof.utils.downloader import Wget, Rsync
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfj', path.join(self.builddir, self.src_file))
            with local.cwd(self.src_dir):
                Rsync(self.fate_uri, self.fate_dir)

    def configure(self):
        from pprof.utils.compiler import lt_clang
        from pprof.utils.run import run

        libav_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
        with local.cwd(libav_dir):
            configure = local["./configure"]
            run(configure["--disable-shared", "--cc=" + str(
                clang), "--extra-ldflags=" + " ".join(self.ldflags),
                          "--samples=" + self.fate_dir])

    def build(self):
        from pprof.utils.run import run
        libav_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(libav_dir):
            run(make["clean", "all"])
