#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
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
            return LibAV(exp, "avconv", "multimedia")
    ProjectFactory.addFactory("LibAV", Factory())


    src_dir = "libav-11.3"
    src_file = src_dir + ".tar.gz"
    src_uri = "https://libav.org/releases/" + src_file
    fate_dir = "fate-samples"
    fate_uri = "rsync://fate-suite.libav.org/fate-suite/"

    def run_tests(self, experiment):
        with local.cwd(self.builddir):
            sh_file = path.join(self.src_dir, self.name)
            with open(sh_file, 'w') as run_f:
                run_f.write("#!/usr/bin/env bash\n")
                run_f.write("{} \"$@\"\n".format(str(experiment)))
            chmod["+x", sh_file] & FG

        with local.cwd(self.src_dir):
            make["V=1", "-i", "fate"] & FG


    def download(self):
        from pprof.utils.downloader import Wget, Rsync
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfz', path.join(self.builddir, self.src_file))
            with local.cwd(self.src_dir):
                Rsync(self.fate_uri, self.fate_dir)

    def configure(self):
        llvm = path.join(config["llvmdir"], "bin")
        llvm_libs = path.join(config["llvmdir"], "lib")

        clang = local[path.join(llvm, "clang")]
        tar_f, _ = path.splitext(self.src_file)
        tar_x, _ = path.splitext(tar_f)
        libav_src = path.join(self.builddir, tar_x)
        configure = local[path.join(libav_src, "configure")]

        with local.cwd(libav_src):
            configure["--extra-cflags=" + " ".join(self.cflags),
                      "--extra-ldflags=" + " ".join(self.ldflags),
                      "--disable-shared",
                      "--cc=" + str(clang),
                      "--samples=" + self.fate_dir] & FG

    def build(self):
        from plumbum.cmd import ln, mv

        llvm = path.join(config["llvmdir"], "bin")
        llvm_libs = path.join(config["llvmdir"], "lib")
        tar_f, _ = path.splitext(self.src_file)
        tar_x, _ = path.splitext(tar_f)
        libav_src = path.join(self.builddir, tar_x)

        with local.cwd(libav_src):
            with local.env(LD_LIBRARY_PATH=llvm_libs):
                #make["clean", "all"] & FG
                make["all"] & FG
                mv[self.name, self.bin_f] & FG
        self.run_f = self.bin_f

