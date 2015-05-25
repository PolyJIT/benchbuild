#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import (ProjectFactory, log_with, log)
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
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

    def clean(self):
        check_f = path.join(self.builddir, self.check_f)
        self.products.add(check_f)

        super(Ccrypt, self).clean()

    src_dir = "ccrypt-1.10"
    src_file = "ccrypt-1.10.tar.gz"
    src_uri = "http://ccrypt.sourceforge.net/download/ccrypt-1.10.tar.gz"

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar, cp

        ccrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfz', path.join(self.builddir, self.src_file))

    def configure(self):
        from pprof.utils.compiler import lt_clang, lt_clang_cxx

        clang = lt_clang(self.cflags)
        clang_cxx = lt_clang_cxx(self.cflags)
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
            make()

    def run_tests(self, experiment):
        from plumbum.cmd import make
        from pprof.project import wrap_tool

        exp = experiment(self.run_f)

        ccrypt_dir = path.join(self.builddir, self.src_dir)
        wrap_tool(path.join(ccrypt_dir, "src", self.name), experiment)
        wrap_tool(path.join(ccrypt_dir, "check", "crypt3-check"), experiment)
        wrap_tool(path.join(ccrypt_dir, "check", "rijndael-check"), experiment)

        with local.cwd(ccrypt_dir):
            make("check")
