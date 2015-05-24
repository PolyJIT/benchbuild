import os
from pprof.settings import config

"""Manage database interaction for pprof
"""


def setup_db_config():
    """Query the environment for database connection information
    """

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
    """Get or create the database connection using the information stored
    in the global config
    """
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


def create_run(conn, cmd, prj, exp, grp):
    """Create a new 'run' in the database. The returned ID from this call
    can be used for subsequent entries into the database.

    :conn: The database connection we should use.
    :cmd: The command that is/has been executed.
    :prj: The project this run belongs to.
    :exp: The experiment this run belongs to.
    :grp: The run_group (uuid) we blong to.
    :returns: an serial identifier for the new run.

    """
    from datetime import datetime
    from psycopg2 import extras, extensions

    extras.register_uuid()

    sql_insert = ("INSERT INTO run (finished, command, project_name, "
                  "experiment_name, run_group, experiment_group) "
                  "VALUES (TIMESTAMP %s, %s, %s, %s, %s, %s) "
                  "RETURNING id;")

    with conn.cursor() as c:
        c.execute(
            sql_insert, (datetime.now(), cmd, prj, exp, extensions.adapt(grp),
                         extensions.adapt(config["experiment"])))
        run_id = c.fetchone()[0]
    conn.commit()
    return run_id
