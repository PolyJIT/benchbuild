#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import cp

class X264(PprofGroup):

    """ x264 """

    inputfiles = ["tbbt-small.y4m"]

    class Factory:
        def create(self, exp):
            obj = X264(exp, "x264", "multimedia")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("X264", Factory())

    def prepare(self):
        super(X264, self).prepare()

        testfiles = [path.join(self.testdir, x) for x in self.inputfiles]
        for testfile in testfiles:
            cp[testfile, self.builddir] & FG

    def clean(self):
        for x in self.inputfiles:
            self.products.add(path.join(self.builddir, x))

        super(X264, self).clean()

    def run(self, experiment):
        testfiles = [path.join(self.testdir, x) for x in self.inputfiles]
        # TODO: Prepare test videos
        for ifile in testfiles:
            with local.cwd(self.builddir):
                experiment[
                    ifile,
                    "--threads", "1",
                    "-o", "/dev/null",
                    "--frames", "5",
                    "--crf", "30",
                    "-b1", "-m1", "-r1", "--me", "dia", "--no-cabac",
                    "--direct", "temporal", "--ssim", "--no-weightb"] & FG
                experiment[
                    ifile,
                    "--threads", "1",
                    "-o", "/dev/null",
                    "--frames", "5",
                    "--crf", "16",
                    "-b2", "-m3", "-r3", "--me", "hex", "--no-8x8dct",
                    "--direct", "spatial", "--no-dct-decimate", "-t0",
                    "--slice-max-mbs", "50"] & FG
                experiment[
                    ifile,
                    "--threads", "1",
                    "-o", "/dev/null",
                    "--frames", "5",
                    "--crf", "26",
                    "-b4", "-m5", "-r2", "--me", "hex", "--cqm", "jvt",
                    "--nr", "100", "--psnr", "--no-mixed-refs",
                    "--b-adapt", "2", "--slice-max-size", "1500"] & FG
                experiment[
                    ifile,
                    "--threads", "1", "-o", "/dev/null", "--frames", "5",
                    "--crf", "18", "-b3", "-m9", "-r5", "--me", "umh",
                    "-t1", "-A", "all", "--b-pyramid", "normal",
                    "--direct", "auto", "--no-fast-pskip", "--no-mbtree"] & FG
                experiment[
                    ifile,
                    "--threads", "1", "-o", "/dev/null", "--frames", "5",
                    "--crf", "22", "-b3", "-m7", "-r4", "--me", "esa", "-t2",
                    "-A", "all", "--psy-rd", "1.0:1.0", "--slices", "4"] & FG
                experiment[
                    ifile,
                    "--threads", "1", "-o", "/dev/null", "--frames", "5",
                    "--crf", "24", "-b3", "-m10", "-r3", "--me", "tesa",
                    "-t2"] & FG
                experiment[
                    ifile,
                    "--threads", "1", "-o", "/dev/null", "--frames", "5",
                    "-q0", "-m9", "-r2", "--me", "hex", "-Aall"] & FG
                experiment[
                    ifile,
                    "--threads", "1", "-o", "/dev/null", "--frames", "5",
                    "-q0", "-m2", "-r1", "--me", "hex", "--no-cabac"] & FG

