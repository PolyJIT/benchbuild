"""
media-video/x264-encoder within gentoo chroot.
"""
from os import path
from benchbuild.utils.wrapping import wrap_in_uchroot as wrap
from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import uretry, uchroot


class X264(GentooGroup):
    """
        media-video/x264-encoder
    """
    NAME = "gentoo-x264"
    DOMAIN = "media-libs"

    test_url = "http://lairosiel.de/dist/"
    inputfiles = {"tbbt-small.y4m": [],
                  "Sintel.2010.720p.raw": ["--input-res", "1280x720"]}

    def prepare(self):
        super(X264, self).prepare()

        for testfile in self.inputfiles:
            Wget(self.test_url + testfile, testfile)

    def build(self):
        emerge_in_chroot = uchroot()["/usr/bin/emerge"]
        uretry(emerge_in_chroot["media-video/x264-encoder"])

    def run_tests(self, experiment, run):
        wrap(
            path.join(self.builddir, "usr/bin/x264"), experiment,
            self.builddir)
        x264 = uchroot()["/usr/bin/x264"]

        tests = [
            "--crf 30 -b1 -m1 -r1 --me dia --no-cabac --direct temporal --ssim --no-weightb",
            "--crf 16 -b2 -m3 -r3 --me hex --no-8x8dct --direct spatial --no-dct-decimate -t0  --slice-max-mbs 50",
            "--crf 26 -b4 -m5 -r2 --me hex --cqm jvt --nr 100 --psnr --no-mixed-refs --b-adapt 2 --slice-max-size 1500",
            "--crf 18 -b3 -m9 -r5 --me umh -t1 -A all --b-pyramid normal --direct auto --no-fast-pskip --no-mbtree",
            "--crf 22 -b3 -m7 -r4 --me esa -t2 -A all --psy-rd 1.0:1.0 --slices 4",
            "--frames 50 --crf 24 -b3 -m10 -r3 --me tesa -t2",
            "--frames 50 -q0 -m9 -r2 --me hex -Aall",
            "--frames 50 -q0 -m2 -r1 --me hex --no-cabac"
        ]

        for ifile in self.inputfiles:
            for _, test in enumerate(tests):
                uretry(x264[ifile, self.inputfiles[ifile], "--threads", "1", "-o",
                            "/dev/null", test.split(" ")])
