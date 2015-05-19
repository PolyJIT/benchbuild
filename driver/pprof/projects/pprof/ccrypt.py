#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import (ProjectFactory, log_with, log,
                           print_libtool_sucks_wrapper)
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
            obj = Ccrypt(exp, "ccrypt", "encryption")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
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
        from plumbum.cmd import wget, tar, cp

        ccrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            wget(self.src_uri)
            tar('xfz', path.join(self.builddir, self.src_file))

    def configure(self):
        ccrypt_dir = path.join(self.builddir, self.src_dir)

        llvm = path.join(config["llvmdir"], "bin")
        llvm_libs = path.join(config["llvmdir"], "lib")
        clang_cxx = local[path.join(llvm, "clang++")]
        clang = local[path.join(llvm, "clang")]

        with local.cwd(self.builddir):
            print_libtool_sucks_wrapper("clang", self.cflags, str(clang))
            print_libtool_sucks_wrapper("clang++", self.cflags, str(clang_cxx))

        clang = local[path.join(self.builddir, "clang")]
        clang_cxx = local[path.join(self.builddir, "clang++")]
        
        with local.cwd(ccrypt_dir):
            configure = local[path.join(ccrypt_dir, "configure")]

            with local.env(CC=str(clang), CXX=str(clang_cxx),
                           LDFLAGS=" ".join(self.ldflags)):
                configure()

    def build(self):
        from plumbum.cmd import make, ln

        ccrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(ccrypt_dir):
            make & FG
        
        with local.cwd(self.builddir):
            ln("-sf", path.join(ccrypt_dir, "src", "ccrypt"), self.run_f)
            

    def run_tests(self, experiment):
        from plumbum.cmd import make, chmod

        ccrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(ccrypt_dir):
            command = " ".join(experiment["-f"].formulate())
            with local.cwd(self.builddir):
                with open(self.bin_f, 'w+') as ccrypt:
                    ccrypt.writelines([ "#!/bin/sh\n", command + " $*\n" ])
                chmod("+x", self.bin_f)

            with local.env(CHECK_CCRYPT=self.bin_f):
                make["CHECK_CCRYPT=" + self.bin_f, "check"] & FG

