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

    @log_with(log)
    def clean(self):
        testfiles = path.join(self.testdir)
        btestfiles = glob(path.join(self.builddir, "*"))

        self.products.add(path.join(self.builddir, "tests"))
        for f in btestfiles:
            if not path.isdir(f):
                self.products.add(f)

        self.products.add(path.join(self.builddir, "Makefile.libav"))
        super(LibAV, self).clean()

    @log_with(log)
    def prepare(self):
        super(LibAV, self).prepare()

        testfiles = glob(path.join(self.testdir, "*"))

        for f in testfiles:
            cp["-a", f, self.builddir] & FG
        cp[path.join(self.sourcedir, "Makefile.libav"), self.builddir] & FG

    @log_with(log)
    def run_tests(self, experiment):
        with local.env(TESTDIR=self.builddir):
            echo["#!/bin/sh"] >> path.join(self.builddir, self.name) & FG
            echo[str(experiment)] >> path.join(self.builddir, self.name) & FG
            chmod["+x", path.join(self.builddir, self.name)] & FG
            make["-i", "-f", "Makefile.libav", "fate"] & FG


    src_file = "libav-11.3.tar.gz"
    src_uri = "https://libav.org/releases/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfz', path.join(self.builddir, self.src_file))

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
                      "--cc=" + str(clang)] & FG

    def build(self):
        llvm = path.join(config["llvmdir"], "bin")
        llvm_libs = path.join(config["llvmdir"], "lib")
        tar_f, _ = path.splitext(self.src_file)
        tar_x, _ = path.splitext(tar_f)
        libav_src = path.join(self.builddir, tar_x)

        with local.cwd(libav_src):
            with local.env(LD_LIBRARY_PATH=llvm_libs):
                make["clean", "all"] & FG

        with local.cwd(self.builddir):
            ln("-sf", path.join(libav_src, "avconv"), self.run_f)

