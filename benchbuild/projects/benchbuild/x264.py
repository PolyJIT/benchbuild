from plumbum import local

import benchbuild as bb
from benchbuild import CFG
from benchbuild.environments.domain import declarative
from benchbuild.source import HTTP, Git
from benchbuild.utils.cmd import make
from benchbuild.utils.settings import get_number_of_jobs


class X264(bb.Project):
    """ x264 """

    NAME = "x264"
    DOMAIN = "multimedia"
    GROUP = 'benchbuild'
    SOURCE = [
        Git(
            remote='https://code.videolan.org/videolan/x264.git',
            local='x264.git',
            refspec='HEAD',
            limit=5
        ),
        HTTP(
            remote={'tbbt-small': 'http://lairosiel.de/dist/tbbt-small.y4m'},
            local='tbbt-small.y4m'
        ),
        HTTP(
            remote={'sintel': 'http://lairosiel.de/dist/Sintel.2010.720p.raw'},
            local='sintel.raw'
        ),
    ]

    CONFIG = {"tbbt-small": [], "sintel": ["--input-res", "1280x720"]}
    CONTAINER = declarative.ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        x264_repo = local.path(self.source_of('x264.git'))
        clang = bb.compiler.cc(self)

        with local.cwd(x264_repo):
            configure = local["./configure"]
            _configure = bb.watch(configure)

            with local.env(CC=str(clang)):
                _configure(
                    "--disable-thread", "--disable-opencl", "--enable-pic"
                )

            _make = bb.watch(make)
            _make("clean", "all", "-j", get_number_of_jobs(CFG))

    def run_tests(self):
        x264_repo = local.path(self.source_of('x264.git'))
        inputfiles = [
            self.source_of('tbbt-small.y4m'),
            self.source_of('sintel.raw')
        ]

        x264 = bb.wrap(x264_repo / "x264", self)
        tests = [
            (
                '--crf 30 -b1 -m1 -r1 --me dia --no-cabac --direct temporal '
                '--ssim --no-weightb'
            ),
            (
                '--crf 16 -b2 -m3 -r3 --me hex --no-8x8dct --direct spatial '
                '--no-dct-decimate -t0  --slice-max-mbs 50'
            ),
            (
                '--crf 26 -b4 -m5 -r2 --me hex --cqm jvt --nr 100 --psnr '
                '--no-mixed-refs --b-adapt 2 --slice-max-size 1500'
            ),
            (
                '--crf 18 -b3 -m9 -r5 --me umh -t1 -A all --b-pyramid normal '
                '--direct auto --no-fast-pskip --no-mbtree'
            ),
            (
                '--crf 22 -b3 -m7 -r4 --me esa -t2 -A all --psy-rd 1.0:1.0 '
                '--slices 4'
            ),
            ('--frames 50 --crf 24 -b3 -m10 -r3 --me tesa -t2'),
            ('--frames 50 -q0 -m9 -r2 --me hex -Aall'),
            ('--frames 50 -q0 -m2 -r1 --me hex --no-cabac'),
        ]

        for testfile in inputfiles:
            for _, test in enumerate(tests):
                _x264 = x264[testfile]
                if testfile in self.CONFIG:
                    _x264 = _x264[self.CONFIG[testfile]]
                _x264 = _x264["--threads", "1", "-o", "/dev/null"]
                _x264 = _x264[test.split(" ")]
                _x264 = bb.watch(_x264)
                _x264()
