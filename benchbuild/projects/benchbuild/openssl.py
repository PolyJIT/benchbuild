from plumbum import local

import benchbuild as bb
from benchbuild.utils import download
from benchbuild.utils.cmd import make, tar


@download.with_wget({
    "2.1.6": "http://ftp.openbsd.org/pub/OpenBSD/LibreSSL/libressl-2.1.6.tar.gz"
})
class LibreSSL(bb.Project):
    """ OpenSSL """

    NAME = 'libressl'
    DOMAIN = 'encryption'
    GROUP = 'benchbuild'
    VERSION = '2.1.6'
    SRC_FILE = "libressl.tar.gz"
    BINARIES = [
        "aeadtest", "aes_wrap", "asn1test", "base64test", "bftest", "bntest",
        "bytestringtest", "casttest", "chachatest", "cipherstest", "cts128test",
        "destest", "dhtest", "dsatest", "ecdhtest", "ecdsatest", "ectest",
        "enginetest", "evptest", "exptest", "gcm128test", "gost2814789t",
        "hmactest", "ideatest", "igetest", "md4test", "md5test", "mdc2test",
        "mont", "pbkdf2", "pkcs7test", "poly1305test", "pq_test", "randtest",
        "rc2test", "rc4test", "rmdtest", "sha1test", "sha256test", "sha512test",
        "shatest", "ssltest", "timingsafe", "utf8test"
    ]

    def compile(self):
        self.download()
        self.cflags += ["-fPIC"]

        clang = bb.compiler.cc(self)

        tar("xfz", self.src_file)
        unpack_dir = bb.path("libressl-{0}".format(self.version))
        configure = local[unpack_dir / "configure"]
        _configure = bb.watch(configure)
        _make = bb.watch(make)

        with bb.cwd(unpack_dir):
            with bb.env(CC=str(clang)):
                _configure("--disable-asm", "--disable-shared",
                           "--enable-static", "--disable-dependency-tracking",
                           "--with-pic=yes")

            _make("-j8")
            make_tests = make["-Ctests", "-j8"]
            _make_tests = bb.watch(make_tests)
            _make_tests(LibreSSL.BINARIES)

    def run_tests(self):
        unpack_dir = bb.path("libressl-{0}".format(self.version))
        with bb.cwd(unpack_dir / "tests"):
            for binary in LibreSSL.BINARIES:
                bb.wrap(bb.cwd / binary, self)

        with bb.cwd(unpack_dir):
            _make = bb.watch(make)
            _make("V=1", "check", "-i")
