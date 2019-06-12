"""
# Actions

Actions are enhanced callables that are used by `Experiments` to define
the order of operations a project is put through when the experiment
executes.


## Example

TODO
```python
```
"""
import abc
import enum
import functools as ft
import itertools
import logging
import multiprocessing as mp
import os
import sys
import textwrap
import traceback
from datetime import datetime

import attr
import sqlalchemy as sa
from plumbum import ProcessExecutionError

from benchbuild import signals
from benchbuild.settings import CFG
from benchbuild.utils import container, db
from benchbuild.utils.cmd import mkdir, rm, rmdir

LOG = logging.getLogger(__name__)


@enum.unique
class StepResult(enum.IntEnum):
    """Result type for action results."""
    UNSET = 0
    OK = 1
    CAN_CONTINUE = 2
    ERROR = 3


def step_has_failed(step_results, error_status=None):
    if not error_status:
        error_status = [StepResult.ERROR, StepResult.CAN_CONTINUE]

    return len(list(filter(lambda res: res in error_status, step_results))) > 0


def num_steps(steps):
    return sum([len(step) for step in steps])


def print_steps(steps):
    print("Number of actions to execute: {}".format(num_steps(steps)))
    print(*steps)


def to_step_result(func):
    """Convert a function return to a list of StepResults.

    All Step subclasses automatically wrap the result of their
    __call__ method's result with this wrapper.
    If the result is not a list of StepResult values, one will
    be generated.

    result of `[StepResult.OK]`, or convert the given result into
    a list.

    Args:
        func: The function to wrap.
    """

    @ft.wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper stub."""
        res = func(*args, **kwargs)
        if not res:
            res = [StepResult.OK]

        if not hasattr(res, "__iter__"):
            res = [res]
        return res

    return wrapper


def prepend_status(func):
    """Prepends the output of `func` with the status."""

    @ft.wraps(func)
    def wrapper(self, *args, **kwargs):
        """Wrapper stub."""
        res = func(self, *args, **kwargs)
        if self.status is not StepResult.UNSET:
            res = "[{status}]".format(status=self.status.name) + res
        return res

    return wrapper


def notify_step_begin_end(func):
    """Print the beginning and the end of a `func`."""

    @ft.wraps(func)
    def wrapper(self, *args, **kwargs):
        """Wrapper stub."""
        cls = self.__class__
        on_step_begin = cls.ON_STEP_BEGIN
        on_step_end = cls.ON_STEP_END

        for begin_listener in on_step_begin:
            begin_listener(self)

        res = func(self, *args, **kwargs)

        for end_listener in on_step_end:
            end_listener(self, func)
        return res

    return wrapper


def log_before_after(name: str, desc: str):
    """Log customized stirng before & after running func."""

    def func_decorator(f):
        """Wrapper stub."""

        @ft.wraps(f)
        def wrapper(*args, **kwargs):
            """Wrapper stub."""
            LOG.info("\n%s - %s", name, desc)
            res = f(*args, **kwargs)
            if StepResult.ERROR not in res:
                LOG.info("%s - OK\n", name)
            else:
                LOG.error("%s - ERROR\n", name)
            return res

        return wrapper

    return func_decorator


class StepClass(abc.ABCMeta):
    """Decorate `steps` with logging and result conversion."""

    def __new__(mcs, name, bases, namespace, **_):
        result = abc.ABCMeta.__new__(mcs, name, bases, dict(namespace))

        NAME = result.NAME
        DESCRIPTION = result.DESCRIPTION
        if NAME and DESCRIPTION:
            result.__call__ = log_before_after(NAME, DESCRIPTION)(
                to_step_result(result.__call__))
        else:
            result.__call__ = to_step_result(result.__call__)

        result.__str__ = prepend_status(result.__str__)
        return result


@attr.s(cmp=False)
class Step(metaclass=StepClass):
    """Base class of a step.

    This stores all common attributes for step classes.
        metaclass ([type], optional): Defaults to StepClass. Takes
            care of wrapping Steps correctly.

    Raises:
        StopIteration: If we do not encapsulate more substeps.
    """

    NAME = None
    DESCRIPTION = None

    ON_STEP_BEGIN = []
    ON_STEP_END = []

    obj = attr.ib(default=None, repr=False)
    action_fn = attr.ib(default=None, repr=False)
    status = attr.ib(default=StepResult.UNSET)

    def __len__(self):
        return 1

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    @notify_step_begin_end
    def __call__(self):
        if not self.action_fn:
            return StepResult.ERROR
        self.action_fn()
        self.status = StepResult.OK
        return StepResult.OK

    def __str__(self, indent=0):
        return textwrap.indent(
            "* {name}: Execute configured action.".format(name=self.obj.name),
            indent * " ")

    def onerror(self):
        Clean(self.obj)()


@attr.s
class Clean(Step):
    NAME = "CLEAN"
    DESCRIPTION = "Cleans the build directory"

    check_empty = attr.ib(default=False)

    @staticmethod
    def clean_mountpoints(root: str):
        """
        Unmount any remaining mountpoints under :root.

        Args:
            root: All UnionFS-mountpoints under this directory will be
                  unmounted.
        """
        import psutil
        umount_paths = []
        real_root = os.path.realpath(root)
        for part in psutil.disk_partitions(all=True):
            if os.path.commonpath([part.mountpoint, real_root]) == real_root:
                if not part.fstype == "fuse.unionfs":
                    LOG.error("NON-UnionFS mountpoint found under %s", root)
                else:
                    umount_paths.append(part.mountpoint)

    @notify_step_begin_end
    def __call__(self):
        if not CFG['clean']:
            LOG.warning("Clean disabled by config.")
            return
        if not self.obj:
            LOG.warning("No object assigned to this action.")
            return
        obj_builddir = os.path.abspath(self.obj.builddir)
        if os.path.exists(obj_builddir):
            LOG.debug("Path %s exists", obj_builddir)
            Clean.clean_mountpoints(obj_builddir)
            if self.check_empty:
                rmdir(obj_builddir, retcode=None)
            else:
                rm("-rf", obj_builddir)
        else:
            LOG.debug("Path %s did not exist anymore", obj_builddir)
        self.status = StepResult.OK

    def __str__(self, indent=0):
        return textwrap.indent(
            "* {0}: Clean the directory: {1}".format(
                self.obj.name, self.obj.builddir), indent * " ")


class MakeBuildDir(Step):
    NAME = "MKDIR"
    DESCRIPTION = "Create the build directory"

    @notify_step_begin_end
    def __call__(self):
        if not self.obj:
            return
        if not os.path.exists(self.obj.builddir):
            mkdir("-p", self.obj.builddir)
        self.status = StepResult.OK

    def __str__(self, indent=0):
        return textwrap.indent(
            "* {0}: Create the build directory".format(self.obj.name),
            indent * " ")


class Compile(Step):
    NAME = "COMPILE"
    DESCRIPTION = "Compile the project"

    def __init__(self, project):
        super(Compile, self).__init__(obj=project, action_fn=project.compile)

    def __str__(self, indent=0):
        return textwrap.indent("* {0}: Compile".format(self.obj.name),
                               indent * " ")


class Run(Step):
    NAME = "RUN"
    DESCRIPTION = "Execute the run action"

    def __init__(self, project):
        super(Run, self).__init__(obj=project, action_fn=project.run)

    @notify_step_begin_end
    def __call__(self):
        if not self.obj:
            return
        if not self.action_fn:
            return

        self.action_fn()
        self.status = StepResult.OK

    def __str__(self, indent=0):
        return textwrap.indent(
            "* {0}: Execute run-time tests.".format(self.obj.name),
            indent * " ")


@attr.s
class Echo(Step):
    NAME = 'ECHO'
    DESCRIPTION = 'Print a message.'

    message = attr.ib(default="")

    def __str__(self, indent=0):
        return textwrap.indent("* echo: {0}".format(self.message),
                               indent * " ")

    @notify_step_begin_end
    def __call__(self):
        LOG.info(self.message)


def run_any_child(child: Step):
    """
    Execute child step.

    Args:
        child: The child step.
    """
    return child()


@attr.s(cmp=False)
class Any(Step):
    NAME = "ANY"
    DESCRIPTION = "Just run all actions, no questions asked."

    actions = attr.ib(default=attr.Factory(list), repr=False, cmp=False)

    def __len__(self):
        return sum([len(x) for x in self.actions]) + 1

    def __iter__(self):
        return self.actions.__iter__()

    @notify_step_begin_end
    def __call__(self):
        length = len(self.actions)
        cnt = 0
        results = [StepResult.OK]
        for a in self.actions:
            cnt = cnt + 1
            result = a()
            results.append(result)

            if StepResult.ERROR in result:
                LOG.warning("%d actions left in queue", length - cnt)
        self.status = StepResult.OK
        if StepResult.ERROR in results:
            self.status = StepResult.CAN_CONTINUE

    def __str__(self, indent=0):
        sub_actns = [a.__str__(indent + 1) for a in self.actions]
        sub_actns = "\n".join(sub_actns)
        return textwrap.indent("* Execute all of:\n" + sub_actns, indent * " ")


@attr.s(cmp=False, hash=True)
class Experiment(Any):
    NAME = "EXPERIMENT"
    DESCRIPTION = "Run a experiment, wrapped in a db transaction"

    def __attrs_post_init__(self):
        self.actions = \
            [Echo(message="Start experiment: {0}".format(self.obj.name))] + \
            self.actions + \
            [Echo(message="Completed experiment: {0}".format(self.obj.name))]

    def begin_transaction(self):
        experiment, session = db.persist_experiment(self.obj)
        if experiment.begin is None:
            experiment.begin = datetime.now()
        else:
            experiment.begin = min(experiment.begin, datetime.now())
        session.add(experiment)
        try:
            session.commit()
        except sa.orm.exc.StaleDataError:
            LOG.error("Transaction isolation level caused a StaleDataError")

        # React to external signals
        signals.handlers.register(Experiment.end_transaction, experiment,
                                  session)

        return experiment, session

    @staticmethod
    def end_transaction(experiment, session):
        try:
            if experiment.end is None:
                experiment.end = datetime.now()
            else:
                experiment.end = max(experiment.end, datetime.now())
            session.add(experiment)
            session.commit()
        except sa.exc.InvalidRequestError as inv_req:
            LOG.error(inv_req)

    def __run_children(self, num_processes: int):
        results = []
        actions = self.actions

        try:
            with mp.Pool(num_processes) as pool:
                results = list(
                    itertools.chain.from_iterable(
                        pool.map(run_any_child, actions)))
        except KeyboardInterrupt:
            LOG.info("Experiment aborting by user request")
            results.append(StepResult.ERROR)
        except Exception:
            LOG.error("Experiment terminates " "because we got an exception:")
            e_type, e_value, e_traceb = sys.exc_info()
            lines = traceback.format_exception(e_type, e_value, e_traceb)
            LOG.error("".join(lines))
            results.append(StepResult.ERROR)
        return results

    @notify_step_begin_end
    def __call__(self):
        results = []
        session = None
        experiment, session = self.begin_transaction()
        try:
            results = self.__run_children(int(CFG["parallel_processes"]))
        finally:
            self.end_transaction(experiment, session)
            signals.handlers.deregister(self.end_transaction)
        self.status = max(results)
        return results

    def __str__(self, indent=0):
        sub_actns = [a.__str__(indent + 1) for a in self.actions]
        sub_actns = "\n".join(sub_actns)
        return textwrap.indent(
            "\nExperiment: {0}\n".format(self.obj.name) + sub_actns,
            indent * " ")


@attr.s
class RequireAll(Step):
    actions = attr.ib(default=attr.Factory(list))

    def __len__(self):
        return sum([len(x) for x in self.actions]) + 1

    def __iter__(self):
        return self.actions.__iter__()

    @notify_step_begin_end
    def __call__(self):
        results = []
        for i, action in enumerate(self.actions):
            try:
                results.extend(action())
            except ProcessExecutionError as proc_ex:
                LOG.error("\n==== ERROR ====")
                LOG.error("Execution of a binary failed in step: %s",
                          str(action))
                LOG.error(str(proc_ex))
                LOG.error("==== ERROR ====\n")
                results.append(StepResult.ERROR)
            except KeyboardInterrupt:
                LOG.info("User requested termination.")
                action.onerror()
                results.append(StepResult.ERROR)
                raise
            except OSError:
                LOG.error(
                    "Exception in step #%d: %s",
                    i,
                    str(action),
                    exc_info=sys.exc_info())
                results.append(StepResult.ERROR)

            if StepResult.ERROR in results:
                LOG.error("Execution of #%d: '%s' failed.", i, str(action))
                LOG.error("'%s' cannot continue.", str(self))
                action.status = StepResult.ERROR
                action.onerror()
                self.status = StepResult.ERROR
                return results

        self.status = StepResult.OK
        return results

    def __str__(self, indent=0):
        sub_actns = [a.__str__(indent + 1) for a in self.actions]
        sub_actns = "\n".join(sub_actns)
        return textwrap.indent("* All required:\n" + sub_actns, indent * " ")


@attr.s
class Containerize(RequireAll):
    NAME = "CONTAINERIZE"
    DESCRITPION = "Redirect into container"

    def requires_redirect(self):
        project = self.obj
        return not container.in_container() and (project.container is not None)

    @notify_step_begin_end
    def __call__(self):
        project = self.obj
        if self.requires_redirect():
            project.redirect()
            self.status = StepResult.OK
        else:
            return super(Containerize, self).__call__()

    def __str__(self, indent=0):
        sub_actns = [a.__str__(indent + 1) for a in self.actions]
        sub_actns = "\n".join(sub_actns)

        if container.in_container():
            return textwrap.indent("* Running inside container:\n" + sub_actns,
                                   indent * " ")

        if self.requires_redirect():
            return textwrap.indent(
                "* Continue inside container:\n" + sub_actns, indent * " ")

        return textwrap.indent("* Running without container:\n" + sub_actns,
                               indent * " ")


class CleanExtra(Step):
    NAME = "CLEAN EXTRA"
    DESCRIPTION = "Cleans the extra directories."

    @notify_step_begin_end
    def __call__(self):
        if not CFG['clean']:
            return StepResult.OK

        paths = CFG["cleanup_paths"].value
        for p in paths:
            if os.path.exists(p):
                rm("-r", p)
        self.status = StepResult.OK

    def __str__(self, indent=0):
        paths = CFG["cleanup_paths"].value
        lines = []
        for p in paths:
            lines.append(
                textwrap.indent("* Clean the directory: {0}".format(p),
                                indent * " "))
        return "\n".join(lines)
