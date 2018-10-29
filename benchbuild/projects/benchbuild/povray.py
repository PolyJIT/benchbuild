from plumbum import FG, local

from benchbuild import project
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import (cp, find, grep, head, make, mkdir, sed, sh,
                                  tar)


@download.with_git('https://github.com/POV-Ray/povray', limit=5)
class Povray(project.Project):
    """ povray benchmark """

    NAME = 'povray'
    DOMAIN = 'multimedia'
    GROUP = 'benchbuild'
    SRC_FILE = 'povray.git'
    VERSION = 'HEAD'

    boost_src_dir = "boost_1_59_0"
    boost_src_file = boost_src_dir + ".tar.bz2"
    boost_src_uri = \
        "http://sourceforge.net/projects/boost/files/boost/1.59.0/" + \
        boost_src_file

    def compile(self):
        self.download()
        download.Wget(self.boost_src_uri, self.boost_src_file)
        tar("xfj", self.boost_src_file)

        cp("-ar", local.path(self.testdir) / "cfg", '.')
        cp("-ar", local.path(self.testdir) / "etc", '.')
        cp("-ar", local.path(self.testdir) / "scenes", '.')
        cp("-ar", local.path(self.testdir) / "share", '.')
        cp("-ar", local.path(self.testdir) / "test", '.')

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)
        # First we have to prepare boost for lady povray...
        boost_prefix = "boost-install"
        with local.cwd(self.boost_src_dir):
            mkdir(boost_prefix)
            bootstrap = local["./bootstrap.sh"]
            run.run(bootstrap["--with-toolset=clang",
                              "--prefix=\"{0}\"".format(boost_prefix)])
            _b2 = local["./b2"]
            run.run(
                _b2["--ignore-site-config", "variant=release", "link=static",
                    "threading=multi", "optimization=speed", "install"])

        src_file = local.path(self.src_file)
        with local.cwd(src_file):
            with local.cwd("unix"):
                sh("prebuild.sh")

            configure = local["./configure"]
            with local.env(
                    COMPILED_BY="BB <no@mail.nono>",
                    CC=str(clang),
                    CXX=str(clang_cxx)):
                run.run(configure["--with-boost=" + boost_prefix])
            run.run(make["all"])

    def run_tests(self, runner):
        povray_binary = local.path(self.src_file) / "unix" / self.name
        tmpdir = local.path("tmp")
        tmpdir.mkdir()

        povini = local.path("cfg") / ".povray" / "3.6" / "povray.ini"
        scene_dir = local.path("share") / "povray-3.6" / "scenes"

        povray = wrapping.wrap(povray_binary, self)
        pov_files = find(scene_dir, "-name", "*.pov").splitlines()
        for pov_f in pov_files:
            with local.env(
                    POVRAY=povray_binary,
                    INSTALL_DIR='.',
                    OUTPUT_DIR=tmpdir,
                    POVINI=povini):
                options = ((((head["-n", "50", "\"" + pov_f + "\""]
                              | grep["-E", "'^//[ ]+[-+]{1}[^ -]'"])
                             | head["-n", "1"]) | sed["s?^//[ ]*??"]) & FG)
                run.run(
                    povray["+L" + scene_dir, "+L" + tmpdir, "-i" +
                           pov_f, "-o" + tmpdir, options, "-p"],
                    retcode=None)
