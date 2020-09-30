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
import enum
import functools as ft
import itertools
import logging
import os
import sys
import textwrap
import traceback
import typing as tp
from datetime import datetime

import attr
import pathos.multiprocessing as mp
import sqlalchemy as sa
from plumbum import ProcessExecutionError

from benchbuild import signals, source
from benchbuild.settings import CFG
from benchbuild.utils import container, db, run
from benchbuild.utils.cmd import mkdir, rm, rmdir

LOG = logging.getLogger(__name__)

ReturnType = tp.TypeVar('ReturnType')
ReturnTypeA = tp.TypeVar('ReturnTypeA')
ReturnTypeB = tp.TypeVar('ReturnTypeB')
DecoratedFunction = tp.Callable[..., ReturnType]
FunctionDecorator = tp.Callable[[DecoratedFunction[ReturnTypeA]],
                                DecoratedFunction[ReturnTypeB]]


@enum.unique
class StepResult(enum.IntEnum):
    """Result type for action results."""
    UNSET = 0
    OK = 1
    CAN_CONTINUE = 2
    ERROR = 3


StepResultList = tp.List[StepResult]
StepResultVariants = tp.Optional[tp.Union[StepResult, StepResultList]]


def step_has_failed(step_results, error_status=None):
    if not error_status:
        error_status = [StepResult.ERROR, StepResult.CAN_CONTINUE]

    return len(list(filter(lambda res: res in error_status, step_results))) > 0


def to_step_result(
    func: DecoratedFunction[StepResultVariants]
) -> StepResultList:
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


def prepend_status(func: DecoratedFunction[str]) -> DecoratedFunction[str]:
    """Prepends the output of `func` with the status."""

    @tp.overload
    def wrapper(self: 'Step', indent: int) -> str:
        ...

    @tp.overload
    def wrapper(self: 'Step') -> str:
        ...

    @ft.wraps(func)
    def wrapper(self, *args, **kwargs):
        """Wrapper stub."""
        res = func(self, *args, **kwargs)
        if self.status is not StepResult.UNSET:
            res = "[{status}]".format(status=self.status.name) + res
        return res

    return wrapper


def notify_step_begin_end(
    func: DecoratedFunction[StepResultVariants]
) -> DecoratedFunction[StepResultVariants]:
    """Print the beginning and the end of a `func`."""

    @ft.wraps(func)
    def wrapper(
        self: 'Step', *args: tp.Any, **kwargs: tp.Any
    ) -> StepResultVariants:
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


def log_before_after(
    name: str, desc: str
) -> FunctionDecorator[StepResultVariants, StepResultVariants]:
    """Log customized string before & after running func."""

    def func_decorator(
        func: DecoratedFunction[StepResultVariants]
    ) -> DecoratedFunction[StepResultVariants]:
        """Wrapper stub."""

        @ft.wraps(func)
        def wrapper(*args: tp.Any, **kwargs: tp.Any) -> tp.List[StepResult]:
            """Wrapper stub."""
            LOG.info("\n%s - %s", name, desc)
            res = func(*args, **kwargs)
            if StepResult.ERROR not in res:
                LOG.info("%s - OK\n", name)
            else:
                LOG.error("%s - ERROR\n", name)
            return res

        return wrapper

    return func_decorator


class StepClass(type):
    """Decorate `steps` with logging and result conversion."""

    def __new__(
        mcs: tp.Type['StepClass'], name: str, bases: tp.Tuple[type, ...],
        attrs: tp.Dict[str, tp.Any]
    ) -> tp.Any:
        if not 'NAME' in attrs:
            raise AttributeError(
                f'{name} does not define a NAME class attribute.'
            )

        if not 'DESCRIPTION' in attrs:
            raise AttributeError(
                f'{name} does not define a DESCRIPTION class attribute.'
            )

        base_has_call = any([hasattr(bt, '__call__') for bt in bases])
        if not (base_has_call or '__call__' in attrs):
            raise AttributeError(f'{name} does not define a __call__ method.')

        base_has_str = any([hasattr(bt, '__call__') for bt in bases])
        if not (base_has_str or '__str__' in attrs):
            raise AttributeError(f'{name} does not define a __str__ method.')

        name_ = attrs['NAME']
        description_ = attrs['DESCRIPTION']

        def base_attr(name: str) -> tp.Any:
            return attrs[name] if name in attrs else [
                base.__dict__[name] for base in bases if name in base.__dict__
            ][0]

        original_call = base_attr('__call__')
        original_str = base_attr('__str__')

        if name_ and description_:
            attrs['__call__'] = log_before_after(name_, description_)(
                to_step_result(original_call)
            )
        else:
            original_call = attrs['__call__']
            attrs['__call__'] = to_step_result(original_call)

        attrs['__str__'] = prepend_status(original_str)

        return super().__new__(mcs, name, bases, attrs)


@attr.s(eq=False)
class Step(metaclass=StepClass):
    """Base class of a step.

    This stores all common attributes for step classes.
        metaclass ([type], optional): Defaults to StepClass. Takes
            care of wrapping Steps correctly.

    Raises:
        StopIteration: If we do not encapsulate more substeps.
    """
    NAME: tp.ClassVar[str] = ""
    DESCRIPTION: tp.ClassVar[str] = ""

    ON_STEP_BEGIN = []
    ON_STEP_END = []

    obj = attr.ib(default=None, repr=False)
    action_fn = attr.ib(default=None, repr=False)
    status = attr.ib(default=StepResult.UNSET)

    def __len__(self) -> int:
        return 1

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    @notify_step_begin_end
    def __call__(self) -> StepResultVariants:
        if not self.action_fn:
            return StepResult.ERROR
        self.action_fn()
        self.status = StepResult.OK
        return StepResult.OK

    def __str__(self, indent: int = 0) -> str:
        return textwrap.indent(
            "* {name}: Execute configured action.".format(name=self.obj.name),
            indent * " "
        )

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
    def __call__(self) -> StepResultVariants:
        if not CFG['clean']:
            LOG.warning("Clean disabled by config.")
            return StepResult.OK
        if not self.obj:
            LOG.warning("No object assigned to this action.")
            return StepResult.ERROR
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
        return self.status

    def __str__(self, indent: int = 0) -> str:
        return textwrap.indent(
            "* {0}: Clean the directory: {1}".format(
                self.obj.name, self.obj.builddir
            ), indent * " "
        )


class MakeBuildDir(Step):
    NAME = "MKDIR"
    DESCRIPTION = "Create the build directory"

    @notify_step_begin_end
    def __call__(self) -> StepResultVariants:
        if not self.obj:
            return StepResult.ERROR
        if not os.path.exists(self.obj.builddir):
            mkdir("-p", self.obj.builddir)
        self.status = StepResult.OK
        return self.status

    def __str__(self, indent: int = 0) -> str:
        return textwrap.indent(
            "* {0}: Create the build directory".format(self.obj.name),
            indent * " "
        )


class Compile(Step):
    NAME = "COMPILE"
    DESCRIPTION = "Compile the project"

    def __init__(self, project):
        super().__init__(obj=project, action_fn=project.compile)

    def __str__(self, indent: int = 0) -> str:
        return textwrap.indent(
            "* {0}: Compile".format(self.obj.name), indent * " "
        )


@attr.s
class Run(Step):
    NAME = "RUN"
    DESCRIPTION = "Execute the run action"

    #FIXME: This cannot be positional/mandatory because we subclass Step.
    project = attr.ib(default=None)
    experiment = attr.ib(default=None)

    @notify_step_begin_end
    def __call__(self):
        group, session = run.begin_run_group(self.project, self.experiment)
        signals.handlers.register(run.fail_run_group, group, session)
        try:
            self.project.run_tests()
            run.end_run_group(group, session)
        except ProcessExecutionError:
            run.fail_run_group(group, session)
            raise
        except KeyboardInterrupt:
            run.fail_run_group(group, session)
            raise
        finally:
            signals.handlers.deregister(run.fail_run_group)

        self.status = StepResult.OK
        return self.status

    def __str__(self, indent: int = 0) -> str:
        return textwrap.indent(
            "* {0}: Execute run-time tests.".format(self.project.name),
            indent * " "
        )


@attr.s
class Echo(Step):
    NAME = 'ECHO'
    DESCRIPTION = 'Print a message.'

    message = attr.ib(default="")

    def __str__(self, indent: int = 0) -> str:
        return textwrap.indent("* echo: {0}".format(self.message), indent * " ")

    @notify_step_begin_end
    def __call__(self) -> StepResultVariants:
        LOG.info(self.message)
        return StepResult.OK


def run_any_child(child: Step) -> tp.List[StepResult]:
    """
    Execute child step.

    Args:
        child: The child step.
    """
    return child()


@attr.s(eq=False)
class Any(Step):
    NAME = "ANY"
    DESCRIPTION = "Just run all actions, no questions asked."

    actions = attr.ib(default=attr.Factory(list), repr=False, eq=False)

    def __len__(self) -> int:
        return sum([len(x) for x in self.actions]) + 1

    def __iter__(self):
        return self.actions.__iter__()

    @notify_step_begin_end
    def __call__(self) -> tp.List[StepResult]:
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
        return results

    def __str__(self, indent: int = 0) -> str:
        sub_actns = [a.__str__(indent + 1) for a in self.actions]
        sub_actns = "\n".join(sub_actns)
        return textwrap.indent("* Execute all of:\n" + sub_actns, indent * " ")


@attr.s(eq=False, hash=True)
class Experiment(Any):
    NAME = "EXPERIMENT"
    DESCRIPTION = "Run a experiment, wrapped in a db transaction"

    def __attrs_post_init__(self):
        if not self.actions:
            return

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
        signals.handlers.register(
            Experiment.end_transaction, experiment, session
        )

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

    def __run_children(self, num_processes: int) -> tp.List[StepResult]:
        results = []
        actions = self.actions

        try:
            with mp.Pool(num_processes) as pool:
                results = list(
                    itertools.chain.from_iterable(
                        pool.map(run_any_child, actions)
                    )
                )
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
    def __call__(self) -> tp.List[StepResult]:
        results = []
        session = None
        experiment, session = self.begin_transaction()
        try:
            results = self.__run_children(int(CFG["parallel_processes"]))
        finally:
            self.end_transaction(experiment, session)
            signals.handlers.deregister(self.end_transaction)
        self.status = max(results) if results else StepResult.OK
        return results

    def __str__(self, indent: int = 0) -> str:
        sub_actns = [a.__str__(indent + 1) for a in self.actions]
        sub_actns = "\n".join(sub_actns)
        return textwrap.indent(
            "\nExperiment: {0}\n".format(self.obj.name) + sub_actns,
            indent * " "
        )


@attr.s
class RequireAll(Step):
    NAME = "REQUIRE ALL"
    DESCRIPTION = "All child steps need to succeed"

    actions = attr.ib(default=attr.Factory(list))

    def __len__(self):
        return sum([len(x) for x in self.actions]) + 1

    def __iter__(self):
        return self.actions.__iter__()

    @notify_step_begin_end
    def __call__(self) -> StepResultVariants:
        results = []
        for i, action in enumerate(self.actions):
            try:
                results.extend(action())
            except ProcessExecutionError as proc_ex:
                LOG.error("\n==== ERROR ====")
                LOG.error(
                    "Execution of a binary failed in step: %s", str(action)
                )
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
                    exc_info=sys.exc_info()
                )
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

    def __str__(self, indent: int = 0) -> str:
        sub_actns = [a.__str__(indent + 1) for a in self.actions]
        sub_actns = "\n".join(sub_actns)
        return textwrap.indent("* All required:\n" + sub_actns, indent * " ")


@attr.s
class Containerize(RequireAll):
    NAME = "CONTAINERIZE"
    DESCRIPTION = "Redirect into container"

    def requires_redirect(self) -> bool:
        project = self.obj
        return not container.in_container() and (project.container is not None)

    @notify_step_begin_end
    def __call__(self) -> StepResultVariants:
        project = self.obj
        if self.requires_redirect():
            project.redirect()
            self.status = StepResult.OK
            return self.status
        return super().__call__()

    def __str__(self, indent: int = 0) -> str:
        sub_actns = [a.__str__(indent + 1) for a in self.actions]

        if container.in_container():
            return textwrap.indent(
                '\n'.join(['* Running inside container:'] + sub_actns),
                indent * " "
            )

        if self.requires_redirect():
            return textwrap.indent(
                '\n'.join(["* Continue inside container:"] + sub_actns),
                indent * " "
            )

        return textwrap.indent(
            '\n'.join(['* Running without container:'] + sub_actns),
            indent * " "
        )


class CleanExtra(Step):
    NAME = "CLEAN EXTRA"
    DESCRIPTION = "Cleans the extra directories."

    @notify_step_begin_end
    def __call__(self) -> StepResult:
        if not CFG['clean']:
            return StepResult.OK

        paths = CFG["cleanup_paths"].value
        for p in paths:
            if os.path.exists(p):
                rm("-r", p)
        self.status = StepResult.OK
        return self.status

    def __str__(self, indent: int = 0) -> str:
        paths = CFG["cleanup_paths"].value
        lines = []
        for p in paths:
            lines.append(
                textwrap.indent(
                    "* Clean the directory: {0}".format(p), indent * " "
                )
            )
        return "\n".join(lines)


class ProjectEnvironment(Step):
    NAME = 'ENV'
    DESCRIPTION = 'Prepare the project environment.'

    @notify_step_begin_end
    def __call__(self) -> None:
        project = self.obj
        prj_vars = project.variant

        for name, variant in prj_vars.items():
            LOG.info("Fetching %s @ %s", str(name), variant.version)
            src = variant.owner
            src.version(project.builddir, variant.version)

    def __str__(self, indent: int = 0) -> str:
        project = self.obj
        variant = project.variant
        version_str = source.to_str(tuple(variant.values()))

        return textwrap.indent(
            "* Project environment for: {} @ {}".format(
                project.name, version_str
            ), indent * " "
        )
