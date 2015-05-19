import os

config = {
    "sourcedir": os.getcwd(),
    "builddir": os.path.join(os.getcwd(), "results"),
    "testdir": os.path.join(os.getcwd(), "./testinputs"),
    "llvmdir": os.path.join(os.getcwd(), "./install"),
    "likwiddir": os.path.join(os.getcwd(), "/usr"),
    "path": os.environ["PATH"],
    "ld_library_path": os.environ["LD_LIBRARY_PATH"]
}


def setup_db_config():
    global config

    config["db_host"] = "localhost"
    config["db_port"] = 49153
    config["db_name"] = "pprof"
    config["db_user"] = "pprof"
    config["db_pass"] = "pprof"

    db_host = os.environ.get("PPROF_DB_HOST")
    if db_host:
        config["db_host"] = db_host

    db_port = os.environ.get("PPROF_DB_PORT")
    if db_port:
        config["db_port"] = db_port

    db_name = os.environ.get("PPROF_DB_NAME")
    if db_name:
        config["db_name"] = db_name

    db_user = os.environ.get("PPROF_DB_USER")
    if db_user:
        config["db_user"] = db_user

    db_pass = os.environ.get("PPROF_DB_PASS")
    if db_pass:
        config["db_pass"] = db_pass


_db_connection = None


def get_db_connection():
    import psycopg2
    global _db_connection
    if not _db_connection:
        setup_db_config()
        _db_connection = psycopg2.connect(
            host=config["db_host"],
            port=config["db_port"],
            user=config["db_user"],
            password=config["db_pass"],
            database=config["db_name"]
        )
    return _db_connection
