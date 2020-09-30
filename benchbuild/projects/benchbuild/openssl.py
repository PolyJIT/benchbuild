from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import HTTP
from benchbuild.utils.cmd import make, tar


class LibreSSL(bb.Project):
    """ OpenSSL """

    NAME = 'libressl'
    DOMAIN = 'encryption'
    GROUP = 'benchbuild'
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
    SOURCE = [
        HTTP(
            remote={
                '2.1.6.': (
                    'http://ftp.openbsd.org/pub/OpenBSD/LibreSSL/'
                    'libressl-2.1.6.tar.gz'
                )
            },
            local='libressl.tar.gz'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        libressl_source = local.path(self.source_of('libressl.tar.gz'))
        libressl_version = self.version_of('libressl.tar.gz')

        self.cflags += ["-fPIC"]

        clang = bb.compiler.cc(self)

        tar("xfz", libressl_source)
        unpack_dir = local.path(f'libressl-{libressl_version}')
        configure = local[unpack_dir / "configure"]
        _configure = bb.watch(configure)
        _make = bb.watch(make)

        with local.cwd(unpack_dir):
            with local.env(CC=str(clang)):
                _configure(
                    "--disable-asm", "--disable-shared", "--enable-static",
                    "--disable-dependency-tracking", "--with-pic=yes"
                )

            _make("-j8")
            make_tests = make["-Ctests", "-j8"]
            _make_tests = bb.watch(make_tests)
            _make_tests(LibreSSL.BINARIES)

    def run_tests(self):
        libressl_version = self.version_of('libressl.tar.gz')
        unpack_dir = local.path(f'libressl-{libressl_version}')
        with local.cwd(unpack_dir / "tests"):
            for binary in LibreSSL.BINARIES:
                bb.wrap(local.cwd / binary, self)

        with local.cwd(unpack_dir):
            _make = bb.watch(make)
            _make("V=1", "check", "-i")
