from pprof.projects.pprof.group import PprofGroup
from os import path
from plumbum import local
from plumbum.cmd import cp


class Bzip2(PprofGroup):
    """ Bzip2 """

    NAME = 'bzip2'
    DOMAIN = 'compression'

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]
    src_dir = "bzip2-1.0.6"
    src_file = src_dir + ".tar.gz"
    src_uri = "http://www.bzip.org/1.0.6/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfz', path.join(self.builddir, self.src_file))

    def configure(self):
        pass

    def build(self):
        from plumbum.cmd import make
        from pprof.utils.compiler import lt_clang
        from pprof.utils.run import run

        bzip2_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
        with local.cwd(bzip2_dir):
            run(make["CC=" + str(clang), "clean", "bzip2"])

    def pull_in_testfiles(self):
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp(testfiles, self.builddir)

    def prepare(self):
        super(Bzip2, self).prepare()
        self.pull_in_testfiles()

    def run_tests(self, experiment):
        from pprof.project import wrap
        from pprof.utils.run import run

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
