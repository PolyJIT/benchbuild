#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log
from pprof.settings import config
from group import PprofGroup

from os import path
from glob import glob

from plumbum import FG, local
from plumbum.cmd import cp, echo, chmod, make


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
        exp = experiment(self.run_f)

        with local.cwd(self.src_dir):
            wrap(self.name, experiment)

        with local.cwd(self.src_dir):
            make["V=1", "-i", "fate"] & FG

    def download(self):
        from pprof.utils.downloader import Wget, Rsync
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfj', path.join(self.builddir, self.src_file))
            with local.cwd(self.src_dir):
                Rsync(self.fate_uri, self.fate_dir)

    def configure(self):
        from pprof.utils.compiler import clang
        llvm = path.join(config["llvmdir"], "bin")
        llvm_libs = path.join(config["llvmdir"], "lib")

        libav_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(libav_dir):
            configure = local["./configure"]
            configure["--extra-cflags=" + " ".join(self.cflags),
                      "--extra-ldflags=" + " ".join(self.ldflags),
                      "--disable-shared",
                      "--cc=" + str(clang()),
                      "--samples=" + self.fate_dir] & FG

    def build(self):
        from plumbum.cmd import ln, mv
        from pprof.utils.compiler import llvm_libs

        libav_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(libav_dir):
            with local.env(LD_LIBRARY_PATH=llvm_libs()):
                make["-j" + config["jobs"], "clean", "all"] & FG
                mv[self.name, self.bin_f] & FG
        self.run_f = self.bin_f
