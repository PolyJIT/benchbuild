"""
Experiment helpers
"""

def handle_stdin(cmd, kwargs):
    """
    Handle stdin for wrapped runtime executors.
    :return:
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

    :marker:
        The marker that limits the time output
    :format_s:
        The format string used to parse the timings
    :ins:
        A list of lines we look for the output.

    :returns:
        A list of timing tuples
    """
    from parse import parse

    timings = [x for x in ins if marker in x]
    res = [parse(format_s, t) for t in timings]
    return filter(None, res)


class GuardedRunException(Exception):

    """
    PPROF Run exception.

    Contains an exception that ocurred during execution of a pprof
    experiment.
    """

    def __init__(self, what, run, session):
        """
        Exception raised when a binary failed to execute properly.

        Args:
            what -- the original exception.
            run -- the run during which we encountered :what.
            session -- the db session we want to log to.
        """
        self.what = what

        if isinstance(what, KeyboardInterrupt):
            session.rollback()

    def __str__(self):
        return self.what.__str__()

    def __repr__(self):
        return self.what.__repr__()


def begin(command, pname, ename, group):
    """
    Begin a run in the database log.

    :command
        The command that will be executed.
    :pname
        The project name we belong to.
    :ename
        The experiment name we belong to.
    :group
        The run group we belong to.
    """
    from pprof.utils.db import create_run
    from pprof.utils import schema as s
    from pprof.settings import config
    from datetime import datetime

    run, session = create_run(command, pname, ename, group)
    log = s.RunLog()
    log.run_id = run.id
    log.begin = datetime.now()
    log.config = str(config)

    session.add(log)
    session.commit()

    return run, session


def end(run, session, stdout, stderr):
    """ End a run in the database log (Successfully). """
    from pprof.utils.schema import RunLog
    from datetime import datetime
    log = session.query(RunLog).filter(RunLog.run_id == run.id).one()
    log.stderr = stderr
    log.stdout = stdout
    log.status = 0
    log.end = datetime.now()
    session.add(log)
    session.commit()


def fail(run, session, retcode, stdout, stderr):
    """ End a run in the database log (Unsuccessfully). """
    from pprof.utils.schema import RunLog
    from datetime import datetime
    log = session.query(RunLog).filter(RunLog.run_id == run.id).one()
    log.stderr = stderr
    log.stdout = stdout
    log.status = retcode
    log.end = datetime.now()
    session.add(log)
    session.commit()


def guarded_exec(cmd, pname, ename, run_group):
    """
    Guard the execution of the given command.

    Args:
        cmd -- the command we guard.
        pname -- the database run we run under.
        ename -- the database session this run belongs to.
        run_group -- the run group this execution will belong to.

    Raises:
        RunException -- If the :cmd encounters an error we wrap the exception
            in a RunException and re-raise. This ends the run unsuccessfully.
    """
    from plumbum.commands import ProcessExecutionError

    run, session = \
        begin(cmd, pname, ename, run_group)
    try:
        retcode, stdout, stderr = cmd.run()
        end(run, session, stdout, stderr)
        return (run, session, retcode, stdout, stderr)
    except ProcessExecutionError as e:
        fail(run, session, e.retcode, e.stdout, e.stderr)
        raise GuardedRunException(e, run, session)


def run(command, retcode=0):
    """
    Execute a plumbum command, depending on the user's settings.
    """
    from plumbum import FG
    command & FG(retcode)
