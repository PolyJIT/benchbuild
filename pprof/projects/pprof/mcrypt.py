from pprof.settings import CFG
from pprof.projects.pprof.group import PprofGroup
from os import path
from plumbum import local


class MCrypt(PprofGroup):
    """ MCrypt benchmark """

    NAME = 'mcrypt'
    DOMAIN = 'encryption'

    src_dir = "mcrypt-2.6.8"
    src_file = src_dir + ".tar.gz"
    src_uri = "http://sourceforge.net/projects/mcrypt/files/MCrypt/2.6.8/" + \
        src_file

    libmcrypt_dir = "libmcrypt-2.5.8"
    libmcrypt_file = libmcrypt_dir + ".tar.gz"
    libmcrypt_uri = "http://sourceforge.net/projects/mcrypt/files/Libmcrypt/2.5.8/" + \
        libmcrypt_file

    mhash_dir = "mhash-0.9.9.9"
    mhash_file = mhash_dir + ".tar.gz"
    mhash_uri = "http://sourceforge.net/projects/mhash/files/mhash/0.9.9.9/" + \
        mhash_file

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfz', self.src_file)

            Wget(self.libmcrypt_uri, self.libmcrypt_file)
            tar('xfz', self.libmcrypt_file)

            Wget(self.mhash_uri, self.mhash_file)
            tar('xfz', self.mhash_file)

    def configure(self):
        from pprof.utils.compiler import lt_clang, lt_clang_cxx
        from pprof.utils.run import run
        from plumbum.cmd import make

        mcrypt_dir = path.join(self.builddir, self.src_dir)
        mhash_dir = path.join(self.builddir, self.mhash_dir)
        libmcrypt_dir = path.join(self.builddir, self.libmcrypt_dir)

        # Build mhash dependency
        with local.cwd(mhash_dir):
            configure = local["./configure"]
            with local.env(CC=lt_clang(self.cflags, self.ldflags,
                                       self.compiler_extension),
                           CXX=lt_clang_cxx(self.cflags, self.ldflags,
                                            self.compiler_extension)):
                run(configure["--prefix=" + self.builddir])
                run(make["-j", CFG["jobs"], "install"])

        # Builder libmcrypt dependency
        with local.cwd(libmcrypt_dir):
            configure = local["./configure"]
            with local.env(CC=lt_clang(self.cflags, self.ldflags,
                                       self.compiler_extension),
                           CXX=lt_clang_cxx(self.cflags, self.ldflags,
                                            self.compiler_extension)):
                run(configure["--prefix=" + self.builddir])
                run(make["-j", CFG["jobs"], "install"])

        with local.cwd(mcrypt_dir):
            configure = local["./configure"]
            with local.env(CC=lt_clang(self.cflags, self.ldflags,
                                       self.compiler_extension),
                           CXX=lt_clang_cxx(self.cflags, self.ldflags,
                                            self.compiler_extension),
                           LD_LIBRARY_PATH=path.join(self.builddir, "lib") +
                           ":" + CFG["ld_library_path"],
                           LDFLAGS="-L" + path.join(self.builddir, "lib"),
                           CFLAGS="-I" + path.join(self.builddir, "include")):
                run(configure["--disable-dependency-tracking",
                              "--enable-static", "--disable-shared",
                              "--with-libmcrypt=" + self.builddir,
                              "--with-libmhash=" + self.builddir])

    def build(self):
        from plumbum.cmd import make
        from pprof.utils.run import run

        mcrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(mcrypt_dir):
            run(make["-j", CFG["jobs"]])

    def run_tests(self, experiment):
        from pprof.project import wrap
        from pprof.utils.run import run

        mcrypt_dir = path.join(self.builddir, self.src_dir, "src", ".libs")
        aestest = wrap(path.join(mcrypt_dir, "lt-aestest"), experiment)
        run(aestest)
        ciphertest = wrap(path.join(mcrypt_dir, "lt-ciphertest"), experiment)
        run(ciphertest)
