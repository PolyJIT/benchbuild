from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.settings import CFG
from benchbuild.source import HTTP
from benchbuild.utils import path
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.settings import get_number_of_jobs


class MCrypt(bb.Project):
    """ MCrypt benchmark """

    NAME = 'mcrypt'
    DOMAIN = 'encryption'
    GROUP = 'benchbuild'
    SOURCE = [
        HTTP(
            remote={
                '2.6.8': (
                    'http://sourceforge.net/projects/mcrypt/files/MCrypt/'
                    '2.6.8/mcrypt-2.6.8.tar.gz'
                )
            },
            local='mcrypt.tar.gz'
        ),
        HTTP(
            remote={
                '2.5.8': (
                    'http://sourceforge.net/projects/mcrypt/files/Libmcrypt/'
                    '2.5.8/libmcrypt-2.5.8.tar.gz'
                )
            },
            local='libmcrypt.tar.gz'
        ),
        HTTP(
            remote={
                '0.9.9.9': (
                    'http://sourceforge.net/projects/mhash/files/mhash/'
                    '0.9.9.9/mhash-0.9.9.9.tar.gz'
                )
            },
            local='mhash.tar.gz'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    libmcrypt_dir = "libmcrypt-2.5.8"
    libmcrypt_file = libmcrypt_dir + ".tar.gz"

    mhash_dir = "mhash-0.9.9.9"
    mhash_file = mhash_dir + ".tar.gz"

    def compile(self):
        mcrypt_source = local.path(self.source_of('mcrypt.tar.gz'))
        libmcrypt_source = local.path(self.source_of('libmcrypt.tar.gz'))
        mhash_source = local.path(self.source_of('mhash.tar.gz'))

        tar('xfz', mcrypt_source)
        tar('xfz', libmcrypt_source)
        tar('xfz', mhash_source)

        builddir = local.path(self.builddir)
        mcrypt_dir = builddir / "mcrypt-2.6.8"
        mhash_dir = builddir / self.mhash_dir
        libmcrypt_dir = builddir / self.libmcrypt_dir

        _cc = bb.compiler.cc(self)
        _cxx = bb.compiler.cxx(self)
        _make = bb.watch(make)

        # Build mhash dependency
        with local.cwd(mhash_dir):
            configure = local["./configure"]
            _configure = bb.watch(configure)

            with local.env(CC=_cc, CXX=_cxx):
                _configure("--prefix=" + builddir)
                _make("-j", get_number_of_jobs(CFG), "install")

        # Builder libmcrypt dependency
        with local.cwd(libmcrypt_dir):
            configure = local["./configure"]
            _configure = bb.watch(configure)
            with local.env(CC=_cc, CXX=_cxx):
                _configure("--prefix=" + builddir)
                _make("-j", CFG["jobs"], "install")

        with local.cwd(mcrypt_dir):
            configure = local["./configure"]
            _configure = bb.watch(configure)
            lib_dir = builddir / "lib"
            inc_dir = builddir / "include"
            env = CFG["env"].value
            mod_env = dict(
                CC=_cc,
                CXX=_cxx,
                LD_LIBRARY_PATH=path.
                list_to_path([str(lib_dir)] + env.get("LD_LIBRARY_PATH", [])),
                LDFLAGS="-L" + str(lib_dir),
                CFLAGS="-I" + str(inc_dir)
            )
            env.update(mod_env)
            with local.env(**env):
                _configure(
                    "--disable-dependency-tracking", "--disable-shared",
                    "--with-libmcrypt=" + builddir,
                    "--with-libmhash=" + builddir
                )
            _make("-j", get_number_of_jobs(CFG))

    def run_tests(self):
        mcrypt_dir = local.path(self.builddir) / "mcrypt-2.6.8"
        mcrypt_libs = mcrypt_dir / "src" / ".libs"

        aestest = bb.wrap(mcrypt_libs / "lt-aestest", self)
        _aestest = bb.watch(aestest)
        _aestest()

        ciphertest = bb.wrap(mcrypt_libs / "lt-ciphertest", self)
        _ciphertest = bb.watch(ciphertest)
        _ciphertest()
