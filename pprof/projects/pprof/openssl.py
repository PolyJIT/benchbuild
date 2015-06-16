#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory
from pprof.settings import config
from pprof.projects.pprof.group import PprofGroup

from os import path
from plumbum import local


class LibreSSL(PprofGroup):

    """ OpenSSL """

    class Factory:

        def create(self, exp):
            return LibreSSL(exp, "libressl", "encryption")
    ProjectFactory.addFactory("LibreSSL", Factory())

    src_dir = "libressl-2.1.6"
    src_file = src_dir + ".tar.gz"
    src_uri = "http://ftp.openbsd.org/pub/OpenBSD/LibreSSL/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar

        openssl_dir = path.join(self.builddir, self.src_file)
        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar("xfz", openssl_dir)

    def configure(self):
        from pprof.utils.compiler import lt_clang
        openssl_dir = path.join(self.builddir, self.src_dir)

        configure = local[path.join(openssl_dir, "configure")]
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags)

        with local.cwd(openssl_dir):
            with local.env(CC=str(clang)):
                configure("--disable-asm")

    def build(self):
        from plumbum.cmd import make

        openssl_dir = path.join(self.builddir, self.src_dir,
        self.compiler_extension)
        with local.cwd(openssl_dir):
            make("-j", config["jobs"], "check")

    def run_tests(self, experiment):
        from plumbum.cmd import find, make
        from pprof.project import wrap

        with local.cwd(path.join(self.src_dir, "tests", ".libs")):
            files = find(".", "-type", "f", "-executable")
            for wrap_f in files.split("\n"):
                if len(wrap_f) > 0:
                    wrap(wrap_f, experiment)
        with local.cwd(self.src_dir):
            make("V=1", "check")
