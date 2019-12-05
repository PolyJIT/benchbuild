from plumbum import local

import benchbuild as bb

from benchbuild.downloads import HTTP
from benchbuild.utils.cmd import make, tar


class LibreSSL(bb.Project):
    """ OpenSSL """

    NAME: str = 'libressl'
    DOMAIN: str = 'encryption'
    GROUP: str = 'benchbuild'
    VERSION: str = '2.1.6'
    BINARIES = [
        "aeadtest", "aes_wrap", "asn1test", "base64test", "bftest", "bntest",
        "bytestringtest", "casttest", "chachatest", "cipherstest",
        "cts128test", "destest", "dhtest", "dsatest", "ecdhtest", "ecdsatest",
        "ectest", "enginetest", "evptest", "exptest", "gcm128test",
        "gost2814789t", "hmactest", "ideatest", "igetest", "md4test",
        "md5test", "mdc2test", "mont", "pbkdf2", "pkcs7test", "poly1305test",
        "pq_test", "randtest", "rc2test", "rc4test", "rmdtest", "sha1test",
        "sha256test", "sha512test", "shatest", "ssltest", "timingsafe",
        "utf8test"
    ]
    SOURCE = [
        HTTP(remote={
            '2.1.6.':
            'http://ftp.openbsd.org/pub/OpenBSD/LibreSSL/libressl-2.1.6.tar.gz'
        },
             local='libressl.tar.gz')
    ]

    def compile(self):
        libressl_source = bb.path(self.source[0].local)

        self.cflags += ["-fPIC"]

        clang = bb.compiler.cc(self)

        tar("xfz", libressl_source)
        unpack_dir = bb.path("libressl-{0}".format(self.version))
        configure = local[unpack_dir / "configure"]
        configure = bb.watch(configure)
        make_ = bb.watch(make)

        with bb.cwd(unpack_dir):
            with bb.env(CC=str(clang)):
                configure("--disable-asm", "--disable-shared",
                          "--enable-static", "--disable-dependency-tracking",
                          "--with-pic=yes")

            make_("-j8")
            make_tests = make["-Ctests", "-j8"]
            make_tests = bb.watch(make_tests)
            make_tests(LibreSSL.BINARIES)

    def run_tests(self):
        unpack_dir = bb.path("libressl-{0}".format(self.version))
        with bb.cwd(unpack_dir / "tests"):
            for binary in LibreSSL.BINARIES:
                bb.wrap(local.cwd / binary, self)

        with bb.cwd(unpack_dir):
            make_ = bb.watch(make)
            make_("V=1", "check", "-i")
