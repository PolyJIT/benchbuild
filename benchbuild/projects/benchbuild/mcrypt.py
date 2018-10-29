from plumbum import local

from benchbuild import project
from benchbuild.settings import CFG
from benchbuild.utils import compiler, download, path, run, wrapping
from benchbuild.utils.cmd import make, tar


@download.with_wget({
    "2.6.8":
    'http://sourceforge.net/'
    'projects/mcrypt/files/MCrypt/2.6.8/mcrypt-2.6.8.tar.gz'
})
class MCrypt(project.Project):
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

        download.Wget(self.libmcrypt_uri, self.libmcrypt_file)
        download.Wget(self.mhash_uri, self.mhash_file)

        tar('xfz', self.src_file)
        tar('xfz', self.libmcrypt_file)
        tar('xfz', self.mhash_file)

        builddir = local.path(self.builddir)
        mcrypt_dir = builddir / "mcrypt-2.6.8"
        mhash_dir = builddir / self.mhash_dir
        libmcrypt_dir = builddir / self.libmcrypt_dir

        _cc = compiler.cc(self)
        _cxx = compiler.cxx(self)

        # Build mhash dependency
        with local.cwd(mhash_dir):
            configure = local["./configure"]
            with local.env(CC=_cc, CXX=_cxx):
                run.run(configure["--prefix=" + builddir])
                run.run(make["-j", CFG["jobs"], "install"])

        # Builder libmcrypt dependency
        with local.cwd(libmcrypt_dir):
            configure = local["./configure"]
            with local.env(CC=_cc, CXX=_cxx):
                run.run(configure["--prefix=" + builddir])
                run.run(make["-j", CFG["jobs"], "install"])

        with local.cwd(mcrypt_dir):
            configure = local["./configure"]
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
                run.run(configure["--disable-dependency-tracking",
                                  "--enable-static", "--disable-shared",
                                  "--with-libmcrypt=" +
                                  builddir, "--with-libmhash=" + builddir])
            run.run(make["-j", CFG["jobs"]])

    def run_tests(self, runner):
        mcrypt_dir = local.path(self.builddir) / "mcrypt-2.6.8"
        mcrypt_libs = mcrypt_dir / "src" / ".libs"
        aestest = wrapping.wrap(mcrypt_libs / "lt-aestest", self)
        ciphertest = wrapping.wrap(mcrypt_libs / "lt-ciphertest", self)
        run.run(aestest)
        run.run(ciphertest)
