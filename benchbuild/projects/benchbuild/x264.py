from plumbum import local

import benchbuild as bb
from benchbuild import CFG
from benchbuild.command import WorkloadSet, Command, SourceRoot
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

    # yapf: disable
    WORKLOADS = {
        WorkloadSet("tbbt-small.y4m"): [
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.y4m", "--threads", "1", "-o", "/dev/null", "--crf", "30", "-b1", "-m1", "-r1", "--me", "dia", "--no-cabac", "--direct", "temporal", "--ssim", "--no-weightb"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.y4m", "--threads", "1", "-o", "/dev/null", "--crf", "16", "-b2", "-m3", "-r3", "--me", "hex", "--no-8x8dct", "--direct", "spatial", "--no-dct-decimate", "-t0", "--slice-max-mbs", "50"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.y4m", "--threads", "1", "-o", "/dev/null", "--crf", "26", "-b4", "-m5", "-r2", "--me", "hex", "--cqm", "jvt", "--nr", "100", "--psnr", "--no-mixed-refs", "--b-adapt", "2", "--slice-max-size", "1500"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.y4m", "--threads", "1", "-o", "/dev/null", "--crf", "18", "-b3", "-m9", "-r5", "--me", "umh", "-t1", "-A", "all", "--b-pyramid", "normal", "--direct", "auto", "--no-fast-pskip", "--no-mbtree"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.y4m", "--threads", "1", "-o", "/dev/null", "--crf", "22", "-b3", "-m7", "-r4", "--me", "esa", "-t2", "-A", "all", "--psy-rd", "1.0:1.0", "--slices", "4"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.y4m", "--threads", "1", "-o", "/dev/null", "--frames", "50", "--crf", "24", "-b3", "-m10", "-r3", "--me", "tesa", "-t2"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.y4m", "--threads", "1", "-o", "/dev/null", "--frames", "50", "-q0", "-m9", "-r2", "--me", "hex", "-Aall"),
            Command(SourceRoot("x264.git") / "x264",
                "tbbt-small.y4m", "--threads", "1", "-o", "/dev/null", "--frames", "50", "-q0", "-m2", "-r1", "--me", "hex", "--no-cabac")
        ],
        WorkloadSet("sintel.raw"): [
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--crf", "30", "-b1", "-m1", "-r1", "--me", "dia", "--no-cabac", "--direct", "temporal", "--ssim", "--no-weightb"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--crf", "16", "-b2", "-m3", "-r3", "--me", "hex", "--no-8x8dct", "--direct", "spatial", "--no-dct-decimate", "-t0", "--slice-max-mbs", "50"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--crf", "26", "-b4", "-m5", "-r2", "--me", "hex", "--cqm", "jvt", "--nr", "100", "--psnr", "--no-mixed-refs", "--b-adapt", "2", "--slice-max-size", "1500"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--crf", "18", "-b3", "-m9", "-r5", "--me", "umh", "-t1", "-A", "all", "--b-pyramid", "normal", "--direct", "auto", "--no-fast-pskip", "--no-mbtree"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--crf", "22", "-b3", "-m7", "-r4", "--me", "esa", "-t2", "-A", "all", "--psy-rd", "1.0:1.0", "--slices", "4"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--frames", "50", "--crf", "24", "-b3", "-m10", "-r3", "--me", "tesa", "-t2"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--frames", "50", "-q0", "-m9", "-r2", "--me", "hex", "-Aall"),
            Command(SourceRoot("x264.git") / "x264",
                "sintel.raw", "--input-res", "1280x720", "--threads", "1", "-o", "/dev/null", "--frames", "50", "-q0", "-m2", "-r1", "--me", "hex", "--no-cabac")
        ]
    }
    # yapf: enable

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
