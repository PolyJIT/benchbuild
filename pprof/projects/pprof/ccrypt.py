#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory
from pprof.projects.pprof.group import PprofGroup

from os import path
from plumbum import local
from plumbum.cmd import ln


class Ccrypt(PprofGroup):

    """ ccrypt benchmark """

    check_f = "check"

    class Factory:

        def create(self, exp):
            return Ccrypt(exp, "ccrypt", "encryption")
    ProjectFactory.addFactory("Ccrypt", Factory())

    def prepare(self):
        super(Ccrypt, self).prepare()
        check_f = path.join(self.testdir, self.check_f)
        ln("-s", check_f, path.join(self.builddir, self.check_f))

    src_dir = "ccrypt-1.10"
    src_file = "ccrypt-1.10.tar.gz"
    src_uri = "http://ccrypt.sourceforge.net/download/ccrypt-1.10.tar.gz"

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar, cp

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfz', path.join(self.builddir, self.src_file))

    def configure(self):
        from pprof.utils.compiler import lt_clang, lt_clang_cxx

        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                     self.compiler_extension)

        ccrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(ccrypt_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang),
                           CXX=str(clang_cxx),
                           LDFLAGS=" ".join(self.ldflags)):
                configure()

    def build(self):
        from plumbum.cmd import make

        ccrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(ccrypt_dir):
            make("check")

    def run_tests(self, experiment):
        from plumbum.cmd import make
        from pprof.project import wrap

        ccrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(ccrypt_dir):
            wrap(path.join(ccrypt_dir, "src", self.name), experiment)
            wrap(path.join(ccrypt_dir, "check", "crypt3-check"), experiment)
            wrap(path.join(ccrypt_dir, "check", "rijndael-check"), experiment)
            make("check")
