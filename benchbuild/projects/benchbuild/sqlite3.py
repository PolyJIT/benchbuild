import benchbuild as bb
from benchbuild.utils import download
from benchbuild.utils.cmd import make, unzip


@download.with_wget(
    {'3080900': 'http://www.sqlite.org/2015/sqlite-amalgamation-3080900.zip'})
class SQLite3(bb.Project):
    """ SQLite3 """

    NAME = 'sqlite3'
    DOMAIN = 'database'
    GROUP = 'benchbuild'
    VERSION = '3080900'
    SRC_FILE = 'sqlite.zip'

    def compile(self):
        self.download()
        unzip(self.src_file)
        unpack_dir = bb.path('sqlite-amalgamation-{0}'.format(self.version))

        SQLite3.fetch_leveldb()

        clang = bb.compiler.cc(self)
        _clang = bb.watch(clang)

        with bb.cwd(unpack_dir):
            _clang("-fPIC", "-I.", "-c", "sqlite3.c")
            _clang("-shared", "-o", "libsqlite3.so", "sqlite3.o", "-ldl")

        self.build_leveldb()

    @staticmethod
    def fetch_leveldb():
        src_uri = "https://github.com/google/leveldb"
        download.Git(src_uri, "leveldb.src")

    def build_leveldb(self):
        sqlite_dir = bb.path('sqlite-amalgamation-{0}'.format(self.version))
        leveldb_dir = "leveldb.src"

        # We need to place sqlite3 in front of all other flags.
        self.ldflags += ["-L{0}".format(sqlite_dir)]
        self.cflags += ["-I{0}".format(sqlite_dir)]
        clang_cxx = bb.compiler.cxx(self)
        clang = bb.compiler.cc(self)

        with bb.cwd(leveldb_dir):
            with bb.env(CXX=str(clang_cxx), CC=str(clang)):
                _make = bb.watch(make)
                _make("clean", "out-static/db_bench_sqlite3")

    def run_tests(self):
        leveldb_dir = bb.path("leveldb.src")
        with bb.cwd(leveldb_dir):
            with bb.env(LD_LIBRARY_PATH=leveldb_dir):
                sqlite = bb.wrap(
                    leveldb_dir / 'out-static' / 'db_bench_sqlite3', self)
                _sqlite = bb.watch(sqlite)
                _sqlite()
