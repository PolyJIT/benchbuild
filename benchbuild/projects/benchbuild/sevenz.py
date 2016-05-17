from benchbuild.projects.benchbuild.group import BenchBuildGroup
from os import path
from plumbum import local


class SevenZip(BenchBuildGroup):
    """ 7Zip """

    NAME = '7z'
    DOMAIN = 'compression'

    def run_tests(self, experiment):
        from benchbuild.project import wrap
        from benchbuild.utils.run import run

        p7z_dir = path.join(self.builddir, self.src_dir)
        exp = wrap(path.join(p7z_dir, "bin", "7za"), experiment)
        run(exp["b", "-mmt1"])

    src_dir = "p7zip_9.38.1"
    src_file = src_dir + "_src_all.tar.bz2"
    src_uri = "http://downloads.sourceforge.net/project/p7zip/p7zip/9.38.1/" + \
        src_file

    def download(self):
        from benchbuild.utils.downloader import Wget
        from plumbum.cmd import tar, cp

        p7z_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfj', path.join(self.builddir, self.src_file))
            cp(
                path.join(p7z_dir, "makefile.linux_clang_amd64_asm"),
                path.join(p7z_dir, "makefile.machine"))

    def configure(self):
        pass

    def build(self):
        from plumbum.cmd import make
        from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
        from benchbuild.utils.run import run

        p7z_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                     self.compiler_extension)

        with local.cwd(p7z_dir):
            run(make["CC=" + str(clang), "CXX=" + str(clang_cxx), "clean",
                     "all"])
