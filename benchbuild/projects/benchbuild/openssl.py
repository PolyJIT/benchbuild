from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class LibreSSL(Project):
    """ OpenSSL """

    NAME = 'libressl'
    DOMAIN = 'encryption'
    GROUP = 'benchbuild'
    VERSION = '2.1.6'

    src_dir = "libressl-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.gz"
    src_uri = "http://ftp.openbsd.org/pub/OpenBSD/LibreSSL/" + SRC_FILE

    BINARIES = [
        "aeadtest", "aes_wrap", "asn1test", "base64test", "bftest",
        "bntest", "bytestringtest", "casttest", "chachatest",
        "cipherstest", "cts128test", "destest", "dhtest", "dsatest",
        "ecdhtest", "ecdsatest", "ectest", "enginetest", "evptest",
        "exptest", "gcm128test", "gost2814789t", "hmactest",
        "ideatest", "igetest", "md4test", "md5test", "mdc2test",
        "mont", "pbkdf2", "pkcs7test", "poly1305test", "pq_test",
        "randtest", "rc2test", "rc4test", "rmdtest", "sha1test",
        "sha256test", "sha512test", "shatest", "ssltest", "timingsafe",
        "utf8test"
    ]

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xfz", self.SRC_FILE)

    def configure(self):
        self.cflags += ["-fPIC"]
        clang = cc(self)
        configure = local[path.join(self.src_dir, "configure")]

        with local.cwd(self.src_dir):
            with local.env(CC=str(clang)):
                run(configure["--disable-asm", "--disable-shared",
                              "--enable-static",
                              "--disable-dependency-tracking",
                              "--with-pic=yes"])

    def build(self):
        with local.cwd(self.src_dir):
            run(make["-j8"])
            make_tests = make["-Ctests", "-j8"]
            run(make_tests[LibreSSL.BINARIES])

    def run_tests(self, runner):
        with local.cwd(path.join(self.src_dir, "tests")):
            for binary in LibreSSL.BINARIES:
                wrap(path.abspath(binary), self)

        with local.cwd(self.src_dir):
            run(make["V=1", "check", "-i"])
