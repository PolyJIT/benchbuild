from os import path

from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Git, Wget
from benchbuild.utils.run import run
from benchbuild.utils.cmd import cp, find, tar, make, rm, head, grep, sed, sh
from benchbuild.utils.cmd import mkdir
from plumbum import FG, local


class Povray(BenchBuildGroup):
    """ povray benchmark """

    NAME = 'povray'
    DOMAIN = 'multimedia'
    SRC_FILE = 'povray.git'

    src_uri = "https://github.com/POV-Ray/povray"
    boost_src_dir = "boost_1_59_0"
    boost_src_file = boost_src_dir + ".tar.bz2"
    boost_src_uri = \
        "http://sourceforge.net/projects/boost/files/boost/1.59.0/" + \
        boost_src_file

    def download(self):
        Wget(self.boost_src_uri, self.boost_src_file)
        Git(self.src_uri, self.SRC_FILE)
        tar("xfj", self.boost_src_file)

    def configure(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)
        # First we have to prepare boost for lady povray...
        boost_prefix = "boost-install"
        with local.cwd(self.boost_src_dir):
            mkdir(boost_prefix)
            bootstrap = local["./bootstrap.sh"]
            run(bootstrap["--with-toolset=clang", "--prefix=\"{0}\"".format(
                boost_prefix)])
            b2 = local["./b2"]
            run(b2["--ignore-site-config", "variant=release", "link=static",
                   "threading=multi", "optimization=speed", "install"])

        with local.cwd(path.join(self.SRC_FILE, "unix")):
            sh("prebuild.sh")

        with local.cwd(self.SRC_FILE):
            configure = local["./configure"]
            with local.env(COMPILED_BY="BB <no@mail.nono>",
                           CC=str(clang),
                           CXX=str(clang_cxx)):
                run(configure["--with-boost=" + boost_prefix])

    def build(self):
        povray_binary = path.join(self.SRC_FILE, "unix", self.name)

        with local.cwd(self.SRC_FILE):
            rm("-f", povray_binary)
            run(make["clean", "all"])

    def prepare(self):
        super(Povray, self).prepare()
        cp("-ar", path.join(self.testdir, "cfg"), '.')
        cp("-ar", path.join(self.testdir, "etc"), '.')
        cp("-ar", path.join(self.testdir, "scenes"), '.')
        cp("-ar", path.join(self.testdir, "share"), '.')
        cp("-ar", path.join(self.testdir, "test"), '.')

    def run_tests(self, experiment, run):
        povray_binary = path.join(self.SRC_FILE, "unix", self.name)
        tmpdir = "tmp"
        povini = path.join("cfg", ".povray", "3.6", "povray.ini")
        scene_dir = path.join("share", "povray-3.6", "scenes")
        mkdir(tmpdir, retcode=None)

        povray = wrap(povray_binary, experiment)

        pov_files = find(scene_dir, "-name", "*.pov").splitlines()
        for pov_f in pov_files:
            with local.env(POVRAY=povray_binary,
                           INSTALL_DIR='.',
                           OUTPUT_DIR=tmpdir,
                           POVINI=povini):
                options = ((((head["-n", "50", "\"" + pov_f + "\""] |
                              grep["-E", "'^//[ ]+[-+]{1}[^ -]'"]) |
                             head["-n", "1"]) | sed["s?^//[ ]*??"]) & FG)
                run(povray["+L" + scene_dir, "+L" + tmpdir, "-i" + pov_f,
                           "-o" + tmpdir, options, "-p"],
                    retcode=None)
