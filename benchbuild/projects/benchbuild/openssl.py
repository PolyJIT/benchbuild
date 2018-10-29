from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make, tar


@download.with_wget({
    "2.1.6":
    "http://ftp.openbsd.org/pub/OpenBSD/LibreSSL/libressl-2.1.6.tar.gz"
})
class LibreSSL(project.Project):
    """ OpenSSL """

    NAME = 'libressl'
    DOMAIN = 'encryption'
    GROUP = 'benchbuild'
    VERSION = '2.1.6'
    SRC_FILE = "libressl.tar.gz"
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

    def compile(self):
        self.download()
        self.cflags += ["-fPIC"]

        clang = compiler.cc(self)

        tar("xfz", self.src_file)
        unpack_dir = local.path("libressl-{0}".format(self.version))
        configure = local[unpack_dir / "configure"]

        with local.cwd(unpack_dir):
            with local.env(CC=str(clang)):
                run.run(configure[
                    "--disable-asm", "--disable-shared", "--enable-static",
                    "--disable-dependency-tracking", "--with-pic=yes"])

            run.run(make["-j8"])
            make_tests = make["-Ctests", "-j8"]
            run.run(make_tests[LibreSSL.BINARIES])

    def run_tests(self, runner):
        unpack_dir = local.path("libressl-{0}".format(self.version))
        with local.cwd(unpack_dir / "tests"):
            for binary in LibreSSL.BINARIES:
                wrapping.wrap(local.cwd / binary, self)

        with local.cwd(unpack_dir):
            runner(make["V=1", "check", "-i"])
