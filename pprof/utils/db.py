"""

Database support module for the pprof study.

"""
import os
from pprof.settings import config
from abc import ABCMeta, abstractproperty


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


def submit(metrics):
    """
    Submit a dictionary of metrics to the database. The dictionary should
    encode all necessary information about the db schema.

    Example:
        {
            "table" : <name>,
            "columns" : [ col1, col2, col3, col4],
            "values" : [ (col1, col2, col3, col4 ), ... ]
        }

    :metrics:
        A dictionary conforming to this format:
        {
            "table" : <name>,
            "columns" : <columns>,
            "values" : [ (col1, col2, col3, col4 ), ... ]
        }
    """
    if not (metrics.has_key("table") and
            metrics.has_key("columns") and
            metrics.has_key("values")):
        raise Exception("Dictionary format not as expected!")

    columns = metrics["columns"]
    query = "INSERT INTO {} (".format(metrics["table"])
    query += "{}".format(columns[0])
    for column in columns[1:]:
        query += ", {}".format(column)
    query += ") "

    value_cnt = len(columns)
    query += " VALUES ( "
    for i in range(value_cnt):
        if i == 0:
            query += "%s"
        else:
            query += ", %s"

    values = metrics["values"]
    query += ");"

    conn = get_db_connection()
    with conn.cursor() as c:
        for value in values:
            c.execute(query, value)
    conn.commit()


class RunResult(object):

    """
    Base class for result submission.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        self.values = []

    @abstractproperty
    def table(self):
        """
        Returns the name of the table we write our values to
        """
        pass

    @abstractproperty
    def columns(self):
        """
        Returns the name of the columns of our table.
        """
        pass

    def append(self, result):
        """
        Append a single value to the result set

        :result: A tuple suitable for sending it to the pprof.utils.db.submit
                 function, e.g. ("colVal1", "colVal2"), if the table of this
                 result supports 2 columns.
        """
        assert isinstance(result, tuple)
        assert len(result) == len(self.columns)
        self.values.append(result)

    def commit(self):
        """
        Commit the stored values to the database.
        """

        if len(self.values) == 0:
            return

        result_dict = {
            "table": self.table,
            "columns": self.columns,
            "values": self.values
        }
        submit(result_dict)
