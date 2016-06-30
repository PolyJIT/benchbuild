from benchbuild.projects.benchbuild.group import BenchBuildGroup
from plumbum import local
from plumbum.cmd import cp
from os import path


class Bzip2(BenchBuildGroup):
    """ Bzip2 """

    NAME = 'bzip2'
    DOMAIN = 'compression'

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]
    src_dir = "bzip2-1.0.6"
    src_file = src_dir + ".tar.gz"
    src_uri = "http://www.bzip.org/1.0.6/" + src_file

    def download(self):
        from benchbuild.utils.downloader import Wget
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfz', path.join(self.builddir, self.src_file))

    def configure(self):
        pass

    def build(self):
        from plumbum.cmd import make
        from benchbuild.utils.compiler import lt_clang
        from benchbuild.utils.run import run

        bzip2_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
        with local.cwd(bzip2_dir):
            run(make["CFLAGS=-O3", "CC=" + str(clang), "clean", "bzip2"])

    def prepare(self):
        super(Bzip2, self).prepare()
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp(testfiles, self.builddir)

    def run_tests(self, experiment):
        from benchbuild.project import wrap
        from benchbuild.utils.run import run

        exp = wrap(path.join(self.src_dir, "bzip2"), experiment)

        # Compress
        run(exp["-f", "-z", "-k", "--best", "text.html"])
        run(exp["-f", "-z", "-k", "--best", "chicken.jpg"])
        run(exp["-f", "-z", "-k", "--best", "control"])
        run(exp["-f", "-z", "-k", "--best", "input.source"])
        run(exp["-f", "-z", "-k", "--best", "liberty.jpg"])

        # Decompress
        run(exp["-f", "-k", "--decompress", "text.html.bz2"])
        run(exp["-f", "-k", "--decompress", "chicken.jpg.bz2"])
        run(exp["-f", "-k", "--decompress", "control.bz2"])
        run(exp["-f", "-k", "--decompress", "input.source.bz2"])
        run(exp["-f", "-k", "--decompress", "liberty.jpg.bz2"])
