from pprof.projects.pprof.group import PprofGroup
from os import path
from plumbum import FG, local
from plumbum.cmd import cp, chmod, find


class Povray(PprofGroup):
    """ povray benchmark """

    NAME = 'povray'
    DOMAIN = 'multimedia'

    src_uri = "https://github.com/POV-Ray/povray"
    src_dir = "povray.git"
    boost_src_dir = "boost_1_59_0"
    boost_src_file = boost_src_dir + ".tar.bz2"
    boost_src_uri = "http://sourceforge.net/projects/boost/files/boost/1.59.0/" + \
        boost_src_file

    def download(self):
        from pprof.utils.downloader import Git, Wget
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.boost_src_uri, self.boost_src_file)
            Git(self.src_uri, self.src_dir)
            tar("xfj", self.boost_src_file)

    def configure(self):
        from pprof.utils.run import run

        # First we have to prepare boost for lady povray...
        boost_dir = path.join(self.builddir, self.boost_src_dir)
        boost_prefix = path.join(self.builddir, "boost-install")
        with local.cwd(boost_dir):
            from plumbum.cmd import mkdir
            mkdir(boost_prefix)
            bootstrap = local["./bootstrap.sh"]
            run(bootstrap["--with-toolset=clang", "--prefix=\"{}\"".format(
                boost_prefix)])
            b2 = local["./b2"]
            run(b2["--ignore-site-config", "variant=release", "link=static",
                   "threading=multi", "optimization=speed", "install"])

        povray_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(path.join(povray_dir, "unix")):
            from plumbum.cmd import sh
            sh("prebuild.sh")

        with local.cwd(povray_dir):
            from pprof.utils.compiler import lt_clang, lt_clang_cxx
            with local.cwd(self.builddir):
                clang = lt_clang(self.cflags, self.ldflags,
                                 self.compiler_extension)
                clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                         self.compiler_extension)
            configure = local["./configure"]
            with local.env(COMPILED_BY="PPROF <no@mail.nono>",
                           CC=str(clang),
                           CXX=str(clang_cxx)):
                run(configure["--with-boost=" + boost_prefix])

    def build(self):
        from plumbum.cmd import make, rm
        from pprof.utils.run import run
        povray_dir = path.join(self.builddir, self.src_dir)
        povray_binary = path.join(povray_dir, "unix", self.name)

        with local.cwd(povray_dir):
            rm("-f", povray_binary)
            run(make["clean", "all"])

    def prepare(self):
        super(Povray, self).prepare()
        cp("-ar", path.join(self.testdir, "cfg"), self.builddir)
        cp("-ar", path.join(self.testdir, "etc"), self.builddir)
        cp("-ar", path.join(self.testdir, "scenes"), self.builddir)
        cp("-ar", path.join(self.testdir, "share"), self.builddir)
        cp("-ar", path.join(self.testdir, "test"), self.builddir)

    def run_tests(self, experiment):
        from plumbum.cmd import mkdir
        from pprof.project import wrap
        from pprof.utils.run import run

        povray_dir = path.join(self.builddir, self.src_dir)
        povray_binary = path.join(povray_dir, "unix", self.name)
        tmpdir = path.join(self.builddir, "tmp")
        povini = path.join(self.builddir, "cfg", ".povray", "3.6",
                           "povray.ini")
        scene_dir = path.join(self.builddir, "share", "povray-3.6", "scenes")
        mkdir(tmpdir, retcode=None)

        povray = wrap(povray_binary, experiment)

        pov_files = find(scene_dir, "-name", "*.pov").splitlines()
        for pov_f in pov_files:
            from plumbum.cmd import head, grep, sed
            with local.env(POVRAY=povray_binary,
                           INSTALL_DIR=self.builddir,
                           OUTPUT_DIR=tmpdir,
                           POVINI=povini):
                options = ((((head["-n", "50", "\"" + pov_f + "\""]
                              | grep["-E", "'^//[ ]+[-+]{1}[^ -]'"])
                             | head["-n", "1"]) | sed["s?^//[ ]*??"]) & FG)
                run(povray["+L" + scene_dir, "+L" + tmpdir, "-i" + pov_f, "-o"
                           + tmpdir, options, "-p"],
                    retcode=None)
