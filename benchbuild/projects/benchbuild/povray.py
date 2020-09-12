from plumbum import FG, local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import HTTP, Git
from benchbuild.utils.cmd import cp, find, grep, head, make, mkdir, sed, sh, tar


class Povray(bb.Project):
    """ povray benchmark """

    NAME = 'povray'
    DOMAIN = 'multimedia'
    GROUP = 'benchbuild'
    SOURCE = [
        Git(remote='https://github.com/POV-Ray/povray', local='povray.git'),
        HTTP(
            remote={
                '1.59.0':
                    'http://sourceforge.net/projects/boost/files/boost/1.59.0/'
                    'boost_1_59_0.tar.bz2'
            },
            local='boost.tar.bz2'
        ),
        HTTP(
            remote={
                '2016-05-povray':
                    'http://lairosiel.de/dist/2016-05-povray.tar.gz'
            },
            local='inputs.tar.gz'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    boost_src_dir = "boost_1_59_0"
    boost_src_file = boost_src_dir + ".tar.bz2"
    boost_src_uri = \
        "http://sourceforge.net/projects/boost/files/boost/1.59.0/" + \
        boost_src_file

    def compile(self):
        povray_repo = local.path(self.source_of('povray.git'))
        boost_source = local.path(self.source_of('boost.tar.bz2'))
        inputs_source = local.path(self.source_of('inputs.tar.gz'))

        tar('xf', boost_source)
        tar('xf', inputs_source)

        inputs_dir = local.path('./povray/')

        cp("-ar", inputs_dir / "cfg", '.')
        cp("-ar", inputs_dir / "etc", '.')
        cp("-ar", inputs_dir / "scenes", '.')
        cp("-ar", inputs_dir / "share", '.')
        cp("-ar", inputs_dir / "test", '.')

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)
        # First we have to prepare boost for lady povray...
        boost_prefix = "boost-install"
        with local.cwd(self.boost_src_dir):
            mkdir(boost_prefix)
            bootstrap = local["./bootstrap.sh"]
            _bootstrap = bb.watch(bootstrap)
            _bootstrap(
                "--with-toolset=clang", "--prefix=\"{0}\"".format(boost_prefix)
            )

            _b2 = bb.watch(local["./b2"])
            _b2(
                "--ignore-site-config", "variant=release", "link=static",
                "threading=multi", "optimization=speed", "install"
            )

        with local.cwd(povray_repo):
            with local.cwd("unix"):
                sh("prebuild.sh")

            configure = local["./configure"]
            _configure = bb.watch(configure)
            with local.env(
                COMPILED_BY="BB <no@mail.nono>",
                CC=str(clang),
                CXX=str(clang_cxx)
            ):
                _configure("--with-boost=" + boost_prefix)
            _make = bb.watch(make)
            _make("all")

    def run_tests(self):
        povray_repo = local.path(self.source_of('povray.git'))
        povray_binary = povray_repo / 'unix' / self.name
        tmpdir = local.path("tmp")
        tmpdir.mkdir()

        povini = local.path("cfg") / ".povray" / "3.6" / "povray.ini"
        scene_dir = local.path("share") / "povray-3.6" / "scenes"

        povray = bb.wrap(povray_binary, self)
        _povray = bb.watch(povray)
        pov_files = find(scene_dir, "-name", "*.pov").splitlines()
        for pov_f in pov_files:
            with local.env(
                POVRAY=povray_binary,
                INSTALL_DIR='.',
                OUTPUT_DIR=tmpdir,
                POVINI=povini
            ):
                options = ((((
                    head["-n", "50", "\"" + pov_f + "\""] |
                    grep["-E", "'^//[ ]+[-+]{1}[^ -]'"]
                ) | head["-n", "1"]) | sed["s?^//[ ]*??"]) & FG)
                _povray(
                    "+L" + scene_dir,
                    "+L" + tmpdir,
                    "-i" + pov_f,
                    "-o" + tmpdir,
                    options,
                    "-p",
                    retcode=None
                )
