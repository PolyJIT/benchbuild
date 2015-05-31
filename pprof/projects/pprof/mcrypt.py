#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local


class MCrypt(PprofGroup):

    """ MCrypt benchmark """

    class Factory:

        def create(self, exp):
            return MCrypt(exp, "mcrypt", "encryption")
    ProjectFactory.addFactory("MCrypt", Factory())

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
        from plumbum.cmd import make
        import os

        mcrypt_dir = path.join(self.builddir, self.src_dir)
        mhash_dir = path.join(self.builddir, self.mhash_dir)
        libmcrypt_dir = path.join(self.builddir, self.libmcrypt_dir)

        # Build mhash dependency
        with local.cwd(mhash_dir):
            configure = local["./configure"]
            with local.env(CC=lt_clang(self.cflags, self.ldflags),
                           CXX=lt_clang_cxx(self.cflags, self.ldflags)):
                configure("--prefix=" + self.builddir)
                make("-j", config["jobs"], "install")

        # Builder libmcrypt dependency
        with local.cwd(libmcrypt_dir):
            configure = local["./configure"]
            with local.env(CC=lt_clang(self.cflags, self.ldflags),
                           CXX=lt_clang_cxx(self.cflags, self.ldflags)):
                configure("--prefix=" + self.builddir)
                make("-j", config["jobs"], "install")

        with local.cwd(mcrypt_dir):
            configure = local["./configure"]
            with local.env(CC=lt_clang(self.cflags, self.ldflags),
                           CXX=lt_clang_cxx(self.cflags, self.ldflags),
                           LD_LIBRARY_PATH=path.join(
                               self.builddir, "lib") + ":" + config["ld_library_path"],
                           LDFLAGS="-L" + path.join(self.builddir, "lib"),
                           CFLAGS="-I" + path.join(self.builddir, "include")):
                configure("--disable-dependency-tracking",
                          "--with-libmhash=" + self.builddir)

    def build(self):
        from plumbum.cmd import make
        mcrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(mcrypt_dir):
            make("-j", config["jobs"])

    def run_tests(self, experiment):
        from pprof.project import wrap

        mcrypt_dir = path.join(self.builddir, self.src_dir, "src", ".libs")
        aestest = wrap(path.join(mcrypt_dir, "lt-aestest"), experiment)()
        ciphertest = wrap(path.join(mcrypt_dir, "lt-ciphertest"), experiment)()

