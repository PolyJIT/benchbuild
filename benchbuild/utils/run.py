"""Experiment helpers."""
import datetime
import functools
import logging
import sys
import typing as t
from contextlib import contextmanager
from typing import Protocol

import attr
from plumbum import TEE, local
from plumbum.commands import ProcessExecutionError
from plumbum.commands.base import BaseCommand

from benchbuild import settings, signals

CommandResult = t.Tuple[int, str, str]


class WatchableCommand(Protocol):

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> CommandResult:
        ...


CFG = settings.CFG
LOG = logging.getLogger(__name__)


@attr.s(eq=False)
class RunInfo:
    """
    Execution context of wrapped binaries.

    Execution of tracked binaries is guarded with this context
    object. In here we store everything about a single binary
    execution for consumption of an experiment.

    Attributes:
        cmd ():
        failed ():
        project ():
        experiment ():
        retcode ():
        stdout ():
        stderr ():
        db_run ():
        session ():
    """

    def __begin(self, command: BaseCommand, project, experiment, group):
        """
        Begin a run in the database log.

        Args:
            command: The command that will be executed.
            project: The project we belong to.
            experiment: The experiment we belong to.
            group: The run group we belong to.

        Returns:
            (run, session), where run is the generated run instance and
            session the associated transaction for later use.
        """
        if not CFG["db"]["enabled"]:
            return

        # pylint: disable=import-outside-toplevel
        from benchbuild.utils import schema as s
        from benchbuild.utils.db import create_run

        db_run, session = create_run(command, project, experiment, group)
        db_run.begin = datetime.datetime.now()
        db_run.status = 'running'
        log = s.RunLog()
        log.run_id = db_run.id
        log.begin = datetime.datetime.now()
        log.config = repr(CFG)
        session.add(log)
        session.add(db_run)

        self.db_run = db_run
        self.session = session

    def __end(self, stdout, stderr):
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
        if not CFG["db"]["enabled"]:
            return

        # pylint: disable=import-outside-toplevel
        from benchbuild.utils.schema import RunLog

        run_id = self.db_run.id

        log = self.session.query(RunLog).filter(RunLog.run_id == run_id).one()
        log.stderr = stderr
        log.stdout = stdout
        log.status = 0
        log.end = datetime.datetime.now()

        self.db_run.end = datetime.datetime.now()
        self.db_run.status = 'completed'
        self.session.add(log)
        self.session.add(self.db_run)

    def __fail(self, retcode, stdout, stderr):
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
        if not CFG["db"]["enabled"]:
            return

        # pylint: disable=import-outside-toplevel
        from benchbuild.utils.schema import RunLog
        run_id = self.db_run.id

        log = self.session.query(RunLog).filter(RunLog.run_id == run_id).one()
        log.stderr = stderr
        log.stdout = stdout
        log.status = retcode
        log.end = datetime.datetime.now()

        self.db_run.end = datetime.datetime.now()
        self.db_run.status = 'failed'
        self.failed = True
        self.session.add(log)
        self.session.add(self.db_run)

    cmd = attr.ib(default=None, repr=False)
    failed = attr.ib(default=False)
    project = attr.ib(default=None, repr=False)
    experiment = attr.ib(default=None, repr=False)
    retcode = attr.ib(default=0)
    stdout = attr.ib(default=attr.Factory(list), repr=False)
    stderr = attr.ib(default=attr.Factory(list), repr=False)

    db_run = attr.ib(init=False, default=None)
    session = attr.ib(init=False, default=None, repr=False)
    payload = attr.ib(init=False, default=None, repr=False)

    def __attrs_post_init__(self):
        self.__begin(
            self.cmd, self.project, self.experiment, self.project.run_uuid
        )
        signals.handlers.register(self.__fail, 15, "SIGTERM", "SIGTERM")

        if CFG["db"]["enabled"]:
            run_id = self.db_run.id
            settings.CFG["db"]["run_id"] = run_id

    def add_payload(self, name, payload):
        if self == payload:
            return
        if not self.payload:
            self.payload = {name: payload}
        else:
            self.payload.update({name: payload})

    @property
    def has_failed(self):
        """Check, whether this run failed."""
        return self.failed

    def __call__(self, *args, expected_retcode=0, ri=None, **kwargs):
        cmd_env = settings.CFG.to_env_dict()

        with local.env(**cmd_env):
            try:
                bin_name = sys.argv[0]
                retcode, stdout, stderr = \
                    self.cmd & TEE(retcode=expected_retcode)
                f_stdout = bin_name + ".stdout"
                f_stderr = bin_name + ".stderr"
                with open(f_stdout, 'w') as fd_stdout:
                    fd_stdout.write(stdout)

                with open(f_stderr, 'w') as fd_stderr:
                    fd_stderr.write(stderr)

                self.retcode = retcode
                self.stdout = stdout
                self.stderr = stderr
                self.__end(str(stdout), str(stderr))
            except ProcessExecutionError as ex:
                self.__fail(ex.retcode, ex.stderr, ex.stdout)
                self.retcode = ex.retcode
                self.stdout = ex.stdout
                self.stderr = ex.stderr

                LOG.debug("Tracked process failed")
                LOG.error(str(ex))
            except KeyboardInterrupt:
                self.retcode = retcode
                self.stdout = stdout
                self.stderr = stderr
                self.__fail(-1, "", "KeyboardInterrupt")
                LOG.warning("Interrupted by user input")
                raise
            finally:
                signals.handlers.deregister(self.__fail)

        return self

    def commit(self):
        if CFG["db"]["enabled"]:
            self.session.commit()


def begin_run_group(project, experiment):
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
    # pylint: disable=import-outside-toplevel
    from benchbuild.utils.db import create_run_group

    group, session = create_run_group(project, experiment)
    group.begin = datetime.datetime.now()
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
    group.end = datetime.datetime.now()
    group.status = 'completed'
    session.commit()


def fail_run_group(group, session):
    """
    End the run_group unsuccessfully.

    Args:
        group: The run_group we want to complete.
        session: The database transaction we will finish.
    """
    group.end = datetime.datetime.now()
    group.status = 'failed'
    session.commit()


def exit_code_from_run_infos(run_infos: t.List[RunInfo]) -> int:
    """Generate a single exit code from a list of RunInfo objects.

    Takes a list of RunInfos and returns the exit code that is furthest away
    from 0.

    Args:
        run_infos (t.List[RunInfo]): [description]

    Returns:
        int: [description]
    """
    assert run_infos is not None

    if not hasattr(run_infos, "__iter__"):
        return run_infos.retcode

    rcs = [ri.retcode for ri in run_infos]
    max_rc = max(rcs)
    min_rc = min(rcs)
    if max_rc == 0:
        return min_rc
    return max_rc


@contextmanager
def track_execution(cmd, project, experiment, **kwargs):
    """Guard the execution of the given command.

    The given command (`cmd`) will be executed inside a database context.
    As soon as you leave the context we will commit the transaction.
    Any necessary modifications to the database can be identified inside
    the context with the RunInfo object.

    Args:
        cmd: The command we guard.
        project: The project we track for.
        experiment: The experiment we track for.

    Yields:
        RunInfo: A context object that carries the necessary
            database transaction.
    """

    runner = RunInfo(cmd=cmd, project=project, experiment=experiment, **kwargs)
    yield runner
    runner.commit()


def watch(command: BaseCommand) -> WatchableCommand:
    """Execute a plumbum command, depending on the user's settings.

    Args:
        command: The plumbumb command to execute.
    """

    def f(*args: t.Any, retcode: int = 0, **kwargs: t.Any) -> CommandResult:
        final_command = command[args]
        buffered = not bool(CFG['force_watch_unbuffered'])
        return t.cast(
            CommandResult,
            final_command.run_tee(retcode=retcode, buffered=buffered, **kwargs)
        )

    return f


def with_env_recursive(cmd: BaseCommand, **envvars: str) -> BaseCommand:
    """
    Recursively updates the environment of cmd and all its subcommands.

    Args:
        cmd - A plumbum command-like object
        **envvars - The environment variables to update

    Returns:
        The updated command.
    """
    # pylint: disable=import-outside-toplevel
    from plumbum.commands.base import BoundCommand, BoundEnvCommand
    if isinstance(cmd, BoundCommand):
        cmd.cmd = with_env_recursive(cmd.cmd, **envvars)
    elif isinstance(cmd, BoundEnvCommand):
        cmd.envvars.update(envvars)
        cmd.cmd = with_env_recursive(cmd.cmd, **envvars)
    return cmd


def in_builddir(sub: str = '.'):
    """
    Decorate a project phase with a local working directory change.

    Args:
        sub: An optional subdirectory to change into.
    """

    def wrap_in_builddir(func):
        """Wrap the function for the new build directory."""

        @functools.wraps(func)
        def wrap_in_builddir_func(self, *args, **kwargs):
            """The actual function inside the wrapper for the new builddir."""
            p = local.path(self.builddir) / sub
            if not p.exists():
                LOG.error("%s does not exist.", p)

            if p == local.cwd:
                LOG.debug("CWD already is %s", p)
                return func(self, *args, *kwargs)
            with local.cwd(p):
                return func(self, *args, **kwargs)

        return wrap_in_builddir_func

    return wrap_in_builddir


def store_config(func):
    """Decorator for storing the configuration in the project's builddir."""

    @functools.wraps(func)
    def wrap_store_config(self, *args, **kwargs):
        """Wrapper that contains the actual storage call for the config."""
        CFG.store(local.path(self.builddir) / ".benchbuild.yml")
        return func(self, *args, **kwargs)

    return wrap_store_config
