"""Database support module for the pprof study."""
from pprof.settings import config
from abc import ABCMeta, abstractproperty
from pprof.experiment import static_var


@static_var("db", None)
def get_db_connection():
    """
    Get or create the database connection.

    :return:
        An established database connection.
    """
    import psycopg2
    import sys
    if get_db_connection.db is None:
        try:
            get_db_connection.db = psycopg2.connect(
                host=config["db_host"],
                port=config["db_port"],
                user=config["db_user"],
                password=config["db_pass"],
                database=config["db_name"]
            )
        except psycopg2.Error, e:
            sys.stderr.write("FATAL: Could not open database connection.\n")
            sys.stderr.write("{}@{}:{} db: {}\n".format(
                config["db_user"], config["db_host"], config["db_port"],
                config["db_name"]))
            sys.stderr.write("Details:\n")
            sys.stderr.write(str(e))
            sys.exit(1)
    return get_db_connection.db


def create_run(cmd, prj, exp, grp):
    """
    Create a new 'run' in the database.

    The returned ID from this call can be used for subsequent entries
    into the database.

    :cmd: The command that has been executed.
    :prj: The project this run belongs to.
    :exp: The experiment this run belongs to.
    :grp: The run_group (uuid) we blong to.
    :returns: an serial identifier for the new run.

    """
    from datetime import datetime
    from psycopg2 import extras, extensions

    conn = get_db_connection()
    extras.register_uuid()

    sql_insert = ("INSERT INTO run (finished, command, project_name, "
                  "experiment_name, run_group, experiment_group) "
                  "VALUES (TIMESTAMP %s, %s, %s, %s, %s, %s) "
                  "RETURNING id;")

    with conn.cursor() as insert:
        insert.execute(sql_insert, (datetime.now(), cmd, prj, exp,
                                    extensions.adapt(grp),
                                    extensions.adapt(config["experiment"])))
        run_id = insert.fetchone()[0]
    conn.commit()
    return run_id


def submit(metrics):
    """
    Submit a dictionary of metrics to the database.

    The dictionary should encode all necessary information about the db
    schema.

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
    assert isinstance(metrics, dict)
    assert "table" in metrics
    assert "columns" in metrics
    assert "values" in metrics

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
    with conn.cursor() as insert:
        for value in values:
            insert.execute(query, value)
    conn.commit()


class RunResult(object):

    """Base class for result submission."""

    __metaclass__ = ABCMeta

    def __init__(self):
        self.values = []

    @abstractproperty
    def table(self):
        """Return the name of the table we write our values to."""
        pass

    @abstractproperty
    def columns(self):
        """Return the name of the columns of our table."""
        pass

    def append(self, result):
        """Append a single value to the result set.

        :result: A tuple suitable for sending it to the pprof.utils.db.submit
                 function, e.g. ("colVal1", "colVal2"), if the table of this
                 result supports 2 columns.
        """
        assert isinstance(result, tuple)
        assert len(result) == len(self.columns)
        self.values.append(result)

    def commit(self):
        """Commit the stored values to the database."""
        if len(self.values) == 0:
            return

        result_dict = {
            "table": self.table,
            "columns": self.columns,
            "values": self.values
        }
        submit(result_dict)


class TimeResult(RunResult):

    """Database result implementation for Raw Runtime experiments."""

    @property
    def table(self):
        return "metrics"

    @property
    def columns(self):
        return ["name", "value", "run_id"]
