from plumbum import local

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import with_wget, Wget
from benchbuild.utils.run import run
from benchbuild.utils.path import list_to_path
from benchbuild.utils.wrapping import wrap


@with_wget({
    "2.6.8":
    "http://sourceforge.net/projects/mcrypt/files/MCrypt/2.6.8/mcrypt-2.6.8.tar.gz"
})
class MCrypt(Project):
    """ MCrypt benchmark """

    NAME = 'mcrypt'
    DOMAIN = 'encryption'
    GROUP = 'benchbuild'
    VERSION = '2.6.8'
    SRC_FILE = "mcrypt.tar.gz"

    libmcrypt_dir = "libmcrypt-2.5.8"
    libmcrypt_file = libmcrypt_dir + ".tar.gz"
    libmcrypt_uri = \
        "http://sourceforge.net/projects/mcrypt/files/Libmcrypt/2.5.8/" + \
        libmcrypt_file

    mhash_dir = "mhash-0.9.9.9"
    mhash_file = mhash_dir + ".tar.gz"
    mhash_uri = "http://sourceforge.net/projects/mhash/files/mhash/0.9.9.9/" + \
        mhash_file

    def compile(self):
        self.download()

        Wget(self.libmcrypt_uri, self.libmcrypt_file)
        Wget(self.mhash_uri, self.mhash_file)

        tar('xfz', self.src_file)
        tar('xfz', self.libmcrypt_file)
        tar('xfz', self.mhash_file)

        builddir = local.path(self.builddir)
        mcrypt_dir = builddir / "mcrypt-2.6.8"
        mhash_dir = builddir / self.mhash_dir
        libmcrypt_dir = builddir / self.libmcrypt_dir

        _cc = cc(self)
        _cxx = cxx(self)

        # Build mhash dependency
        with local.cwd(mhash_dir):
            configure = local["./configure"]
            with local.env(CC=_cc, CXX=_cxx):
                run(configure["--prefix=" + builddir])
                run(make["-j", CFG["jobs"], "install"])

        # Builder libmcrypt dependency
        with local.cwd(libmcrypt_dir):
            configure = local["./configure"]
            with local.env(CC=_cc, CXX=_cxx):
                run(configure["--prefix=" + builddir])
                run(make["-j", CFG["jobs"], "install"])

        with local.cwd(mcrypt_dir):
            configure = local["./configure"]
            lib_dir = builddir / "lib"
            inc_dir = builddir / "include"
            env = CFG["env"].value()
            mod_env = dict(
                CC=cc,
                CXX=cxx,
                LD_LIBRARY_PATH=list_to_path([str(lib_dir)] +
                                             env.get("LD_LIBRARY_PATH", [])),
                LDFLAGS="-L" + str(lib_dir),
                CFLAGS="-I" + str(inc_dir))
            env.update(mod_env)
            with local.env(**env):
                run(configure["--disable-dependency-tracking",
                              "--enable-static", "--disable-shared",
                              "--with-libmcrypt=" +
                              builddir, "--with-libmhash=" + builddir])
            run(make["-j", CFG["jobs"]])

    def run_tests(self, runner):
        mcrypt_dir = local.path(self.builddir) / "mcrypt-2.6.8"
        mcrypt_libs = mcrypt_dir / "src" / ".libs"
        aestest = wrap(mcrypt_libs / "lt-aestest", self)
        ciphertest = wrap(mcrypt_libs / "lt-ciphertest", self)
        run(aestest)
        run(ciphertest)
