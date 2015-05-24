#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import Project, ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from glob import glob
from plumbum import FG, local

class OpenSSLGroup(Project):

    """ OpenSSL """

    def __init__(self, exp, name):
        super(OpenSSLGroup, self).__init__(exp, name, "encryption", "openssl")
        self.sourcedir = path.join(config["sourcedir"], "src", "openssl", name)
        self.setup_derived_filenames()
        self.calls_f = path.join(self.builddir, "papi.calls.out")
        self.prof_f = path.join(self.builddir, "papi.profile.out")

    src_dir = "libressl-2.1.6"
    src_file = src_dir + ".tar.gz"
    src_uri = "http://ftp.openbsd.org/pub/OpenBSD/LibreSSL/" + src_file
    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import wget, tar

        openssl_dir = path.join(self.builddir, self.src_file)
        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar("xfz", openssl_dir)

    def configure(self):
        from pprof.utils.compiler import clang
        openssl_dir = path.join(self.builddir, self.src_dir)

        configure = local[path.join(openssl_dir, "configure")]
        with local.cwd(openssl_dir):
            cflags = " ".join(self.cflags)
            ldflags = " ".join(self.ldflags)

            with local.env(CFLAGS=cflags, LDFLAGS=ldflags, CC=str(clang())):
                configure("--disable-asm")

    def build(self):
        from plumbum.cmd import make, ln

        openssl_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(openssl_dir):
            make()

class Blowfish(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return Blowfish(exp, "blowfish")
    ProjectFactory.addFactory("Blowfish", Factory())


class Bn(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return Bn(exp, "bn")
    ProjectFactory.addFactory("Bn", Factory())


class Cast(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return Cast(exp, "cast")
    ProjectFactory.addFactory("Cast", Factory())


class DES(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return DES(exp, "des")
    ProjectFactory.addFactory("DES", Factory())


class DSA(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return DSA(exp, "dsa")
    ProjectFactory.addFactory("DSA", Factory())


class ECDSA(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return ECDSA(exp, "ecdsa")
    ProjectFactory.addFactory("ECDSA", Factory())


class HMAC(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return HMAC(exp, "hmac")
    ProjectFactory.addFactory("HMAC", Factory())


class MD5(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return MD5(exp, "md5")
    ProjectFactory.addFactory("MD5", Factory())


class RC4(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return RC4(exp, "rc4")
    ProjectFactory.addFactory("RC4", Factory())


class RSA(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return RSA(exp, "rsa")
    ProjectFactory.addFactory("RSA", Factory())


class SHA1(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return SHA1(exp, "sha1")
    ProjectFactory.addFactory("SHA1", Factory())


class SHA256(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return SHA256(exp, "sha256")
    ProjectFactory.addFactory("SHA256", Factory())


class SHA512(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return SHA512(exp, "sha512")
    ProjectFactory.addFactory("SHA512", Factory())


class SSL(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return SSL(exp, "ssl")

    def run_tests(self, experiment):
        exp = experiment(self.run_f)

        ssl = exp["-time", "-cert",
                path.join(self.sourcedir, "server.pem"),
                "-num", 10000, "-named_curve", "c2tnb431r1",
                "-bytes", 20480]
        with local.cwd(self.builddir):
            ssl["-tls1"] & FG
            ssl["-ssl2"] & FG

    ProjectFactory.addFactory("SSL", Factory())

class OpenSSL(OpenSSLGroup):
    """ OpenSSL benchmark """

    class Factory:
        def create(self, exp):
            return OpenSSL(exp, "openssl")
    ProjectFactory.addFactory("OpenSSL", Factory())

    def run_tests(self, experiment):
        exp = experiment(self.run_f)

        with local.env(OPENSSL_CONF=path.join(self.testdir, "openssl.cnf")):
            certs = path.join(self.testdir, "certs", "demo")
            print certs
            for f in glob(path.join(certs, "*.pem")):
                print f
                super(OpenSSL, self).run(
                    exp["verify", "-CApath", certs, f])

