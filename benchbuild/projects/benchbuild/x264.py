from plumbum import local

import benchbuild as bb
from benchbuild import CFG

from benchbuild.downloads import Git, HTTP
from benchbuild.utils.cmd import cp, make


class X264(bb.Project):
    """ x264 """

    NAME: str = "x264"
    DOMAIN: str = "multimedia"
    GROUP: str = 'benchbuild'
    VERSION: str = 'HEAD'
    SOURCE = [
        Git(remote='git://git.videolan.org/x264.git',
            local='x264.git',
            refspec='HEAD',
            limit=5),
        HTTP(remote={'tbbt-small': 'http://lairosiel.de/dist/tbbt-small.y4m'},
             local='tbbt-small.y4m'),
        HTTP(
            remote={'sintel': 'http://lairosiel.de/dist/Sintel.2010.720p.raw'},
            local='sintel.raw'),
    ]

    inputfiles = {
        "tbbt-small.y4m": [],
        "Sintel.2010.720p.raw": ["--input-res", "1280x720"]
    }

    def compile(self):
        x264_repo = variants.to_source('x264.git', self.variant).local
        clang = compiler.cc(self)

        with local.cwd(x264_repo):
            configure = local["./configure"]
            configure = run.watch(configure)

            with local.env(CC=str(clang)):
                configure("--disable-thread", "--disable-opencl",
                          "--enable-pic")

            make_ = run.watch(make)
            make_("clean", "all", "-j", CFG["jobs"])

    def run_tests(self):
        x264_repo = variants.to_source('x264.git', self.variant).local
        inputfiles = [
            variants.to_source('tbbt-small', self.variant).local,
            variants.to_source('sintel', self.variant).local
        ]

        x264 = wrapping.wrap(x264_repo / "x264", self)
        x264 = run.watch(x264)

        tests = [
            "--crf 30 -b1 -m1 -r1 --me dia --no-cabac --direct temporal --ssim --no-weightb",
            "--crf 16 -b2 -m3 -r3 --me hex --no-8x8dct --direct spatial --no-dct-decimate -t0  --slice-max-mbs 50",
            "--crf 26 -b4 -m5 -r2 --me hex --cqm jvt --nr 100 --psnr --no-mixed-refs --b-adapt 2 --slice-max-size 1500",
            "--crf 18 -b3 -m9 -r5 --me umh -t1 -A all --b-pyramid normal --direct auto --no-fast-pskip --no-mbtree",
            "--crf 22 -b3 -m7 -r4 --me esa -t2 -A all --psy-rd 1.0:1.0 --slices 4",
            "--frames 50 --crf 24 -b3 -m10 -r3 --me tesa -t2",
            "--frames 50 -q0 -m9 -r2 --me hex -Aall",
            "--frames 50 -q0 -m2 -r1 --me hex --no-cabac",
        ]

        for testfile in inputfiles:
            for _, test in enumerate(tests):
                x264(testfile, "--threads", "1", "-o", "/dev/null",
                    test.split(" "))
