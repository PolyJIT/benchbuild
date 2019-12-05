from plumbum import local

from benchbuild import project
from benchbuild.downloads import HTTP
from benchbuild.settings import CFG
from benchbuild.utils import compiler, path, run, wrapping
from benchbuild.utils.cmd import make, tar


class MCrypt(project.Project):
    """ MCrypt benchmark """

    VERSION = '2.6.8'
    NAME: str = 'mcrypt'
    DOMAIN: str = 'encryption'
    GROUP: str = 'benchbuild'
    SOURCE = [
        HTTP(remote={
            '2.6.8':
            'http://sourceforge.net/projects/mcrypt/files/MCrypt/2.6.8/mcrypt-2.6.8.tar.gz'
        },
             local='mcrypt.tar.gz'),
        HTTP(remote={
            '2.5.8':
            'http://sourceforge.net/projects/mcrypt/files/Libmcrypt/2.5.8/libmcrypt-2.5.8.tar.gz'
        },
             local='libmcrypt.tar.gz'),
        HTTP(remote={
            '0.9.9.9':
            'http://sourceforge.net/projects/mhash/files/mhash/0.9.9.9/mhash-0.9.9.9.tar.gz'
        },
             local='mhash.tar.gz')
    ]

    libmcrypt_dir = "libmcrypt-2.5.8"
    libmcrypt_file = libmcrypt_dir + ".tar.gz"

    mhash_dir = "mhash-0.9.9.9"
    mhash_file = mhash_dir + ".tar.gz"

    def compile(self):
        mcrypt_source = local.path(self.source[0].local)
        libmcrypt_source = local.path(self.source[1].local)
        mhash_source = local.path(self.source[2].local)

        tar('xfz', mcrypt_source)
        tar('xfz', libmcrypt_source)
        tar('xfz', mhash_source)

        builddir = local.path(self.builddir)
        mcrypt_dir = builddir / "mcrypt-2.6.8"
        mhash_dir = builddir / self.mhash_dir
        libmcrypt_dir = builddir / self.libmcrypt_dir

        _cc = compiler.cc(self)
        _cxx = compiler.cxx(self)
        make_ = run.watch(make)

        # Build mhash dependency
        with local.cwd(mhash_dir):
            configure = local["./configure"]
            configure = run.watch(configure)

            with local.env(CC=_cc, CXX=_cxx):
                configure("--prefix=" + builddir)
                make_("-j", CFG["jobs"], "install")

        # Builder libmcrypt dependency
        with local.cwd(libmcrypt_dir):
            configure = local["./configure"]
            configure = run.watch(configure)
            with local.env(CC=_cc, CXX=_cxx):
                configure("--prefix=" + builddir)
                make_("-j", CFG["jobs"], "install")

        with local.cwd(mcrypt_dir):
            configure = local["./configure"]
            configure = run.watch(configure)
            lib_dir = builddir / "lib"
            inc_dir = builddir / "include"
            env = CFG["env"].value
            mod_env = dict(
                CC=_cc,
                CXX=_cxx,
                LD_LIBRARY_PATH=path.list_to_path(
                    [str(lib_dir)] + env.get("LD_LIBRARY_PATH", [])),
                LDFLAGS="-L" + str(lib_dir),
                CFLAGS="-I" + str(inc_dir))
            env.update(mod_env)
            with local.env(**env):
                configure("--disable-dependency-tracking", "--enable-static",
                          "--disable-shared", "--with-libmcrypt=" + builddir,
                          "--with-libmhash=" + builddir)
            make_("-j", CFG["jobs"])

    def run_tests(self):
        mcrypt_dir = local.path(self.builddir) / "mcrypt-2.6.8"
        mcrypt_libs = mcrypt_dir / "src" / ".libs"

        aestest = wrapping.wrap(mcrypt_libs / "lt-aestest", self)
        aestest = run.watch(aestest)
        aestest()

        ciphertest = wrapping.wrap(mcrypt_libs / "lt-ciphertest", self)
        ciphertest = run.watch(ciphertest)
        ciphertest()
