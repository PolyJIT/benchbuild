"""
Experiment helpers
"""


def handle_stdin(cmd, kwargs):
    """
    Handle stdin for wrapped runtime executors.

    This little helper checks the kwargs for a `has_stdin` key containing
    a boolean value. If necessary it will pipe in the stdin of this process
    into the plumbum command.

    Args:
        cmd (plumbum.cmd): Command to wrap a stdin handler around.
        kwargs: Dictionary containing the kwargs.
            We check for they key `has_stdin`

    Returns:
        A new plumbum command that deals with stdin redirection, if needed.
    """
    assert isinstance(kwargs, dict)
    import sys

    has_stdin = kwargs.get("has_stdin", False)
    if has_stdin:
        run_cmd = (cmd < sys.stdin)
    else:
        run_cmd = cmd

    return run_cmd


def fetch_time_output(marker, format_s, ins):
    """
    Fetch the output /usr/bin/time from a.

    Args:
        marker: The marker that limits the time output
        format_s: The format string used to parse the timings
        ins: A list of lines we look for the output.

    Returns:
        A list of timing tuples
    """
    from parse import parse

    timings = [x for x in ins if marker in x]
    res = [parse(format_s, t) for t in timings]
    return [_f for _f in res if _f]


class GuardedRunException(Exception):
    """
    PPROF Run exception.

    Contains an exception that ocurred during execution of a pprof
    experiment.
    """

    def __init__(self, what, db_run, session):
        """
        Exception raised when a binary failed to execute properly.

        Args:
            what: the original exception.
            run: the run during which we encountered ``what``.
            session: the db session we want to log to.
        """
        super(GuardedRunException, self).__init__()

        self.what = what
        self.run = db_run

        if isinstance(what, KeyboardInterrupt):
            session.rollback()

    def __str__(self):
        return self.what.__str__()

    def __repr__(self):
        return self.what.__repr__()


def begin_run_group(project):
    """
    Begin a run_group in the database.

    A run_group groups a set of runs for a given project. This models a series
    of runs that form a complete binary runtime test.

    Args:
        project: The project we begin a new run_group for.

    Returns:
        ``(group, session)`` where group is the created group in the
        database and session is the database session this group lives in.
    """
    from pprof.utils.db import create_run_group
    from datetime import datetime

    group, session = create_run_group(project)
    group.begin = datetime.now()
    group.status = 'running'

    session.commit()
    return group, session


def end_run_group(group, session):
    """
    End the run_group successfully.

    Args:
        group: The run_group we want to complete.
        session: The database transaction we will finish.
    """
    from datetime import datetime

    group.end = datetime.now()
    group.status = 'completed'
    session.commit()


def fail_run_group(group, session):
    """
    End the run_group unsuccessfully.

    Args:
        group: The run_group we want to complete.
        session: The database transaction we will finish.
    """
    from datetime import datetime

    group.end = datetime.now()
    group.status = 'failed'
    session.commit()


def begin(command, pname, ename, group):
    """
    Begin a run in the database log.

    Args:
        command: The command that will be executed.
        pname: The project name we belong to.
        ename: The experiment name we belong to.
        group: The run group we belong to.

    Returns:
        (run, session), where run is the generated run instance and session the
        associated transaction for later use.
    """
    from pprof.utils.db import create_run
    from pprof.utils import schema as s
    from pprof.settings import config
    from datetime import datetime

    db_run, session = create_run(command, pname, ename, group)
    db_run.begin = datetime.now()
    db_run.status = 'running'
    log = s.RunLog()
    log.run_id = db_run.id
    log.begin = datetime.now()
    log.config = str(config)

    session.add(log)
    session.commit()

    return db_run, session


def end(db_run, session, stdout, stderr):
    """
    End a run in the database log (Successfully).

    This will persist the log information in the database and commit the
    transaction.

    Args:
        db_run: The ``run`` schema object we belong to
        session: The db transaction we belong to.
        stdout: The stdout we captured of the run.
        stderr: The stderr we capture of the run.
    """
    from pprof.utils.schema import RunLog
    from datetime import datetime
    log = session.query(RunLog).filter(RunLog.run_id == db_run.id).one()
    log.stderr = stderr
    log.stdout = stdout
    log.status = 0
    log.end = datetime.now()
    run.end = datetime.now()
    run.status = 'completed'
    session.add(log)
    session.commit()


def fail(db_run, session, retcode, stdout, stderr):
    """
    End a run in the database log (Unsuccessfully).

    This will persist the log information in the database and commit the
    transaction.

    Args:
        db_run: The ``run`` schema object we belong to
        session: The db transaction we belong to.
        retcode: The return code we captured of the run.
        stdout: The stdout we captured of the run.
        stderr: The stderr we capture of the run.
    """
    from pprof.utils.schema import RunLog
    from datetime import datetime
    log = session.query(RunLog).filter(RunLog.run_id == db_run.id).one()
    log.stderr = stderr
    log.stdout = stdout
    log.status = retcode
    log.end = datetime.now()
    db_run.end = datetime.now()
    db_run.status = 'failed'
    session.add(log)
    session.commit()


def guarded_exec(cmd, pname, ename, run_group):
    """
    Guard the execution of the given command.

    Args:
        cmd: the command we guard.
        pname: the database run we run under.
        ename: the database session this run belongs to.
        run_group: the run group this execution will belong to.

    Raises:
        RunException: If the ``cmd`` encounters an error we wrap the exception
            in a RunException and re-raise. This ends the run unsuccessfully.
    """
    from plumbum.commands import ProcessExecutionError
    from plumbum import local
    from logging import warn

    db_run, session = begin(cmd, pname, ename, run_group)
    try:
        with local.env(PPROF_DB_RUN_ID=db_run.id):
            retcode, stdout, stderr = cmd.run()
        end(db_run, session, stdout, stderr)
        return (db_run, session, retcode, stdout, stderr)
    except ProcessExecutionError as proc_ex:
        fail(db_run, session, proc_ex.retcode, proc_ex.stdout, proc_ex.stderr)
        raise GuardedRunException(proc_ex, db_run, session)
    except KeyboardInterrupt as key_int:
        fail(db_run, session, -1, "", "KeyboardInterrupt")
        warn("Interrupted by user input")
        raise key_int


def run(command, retcode=0):
    """
    Execute a plumbum command, depending on the user's settings.

    Args:
        command: The plumbumb command to execute.
    """
    from logging import error
    from plumbum import FG
    try:
        command & FG(retcode)
    except KeyboardInterrupt as key_int:
        error("Interrupted by user input")
        raise key_int
    except Exception as exception:
        error("Exception:")
        error("   | {}".format(exception))
        raise GuardedRunException(exception, None, None)

def uchroot():
    """
    Returns a uchroot command which can be called with other args to be
            executed in the uchroot.
    Return:
        chroot_cmd
    """
    from pprof.settings import config
    from plumbum.cmd import mkdir
    from plumbum import local

    mkdir("-p", "llvm")
    uchroot_cmd = local["./uchroot"]
    return uchroot_cmd["-C", "-w", "/", "-r", ".", "-m", config["llvmdir"] +
                   ":llvm", "-u", "0", "-g", "0", "--"]
