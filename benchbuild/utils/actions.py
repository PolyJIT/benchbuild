"""# Actions

Actions are enhanced callables that are used by `Experiments` to define
the order of operations a project is put through when the experiment
executes.


## Example

TODO
```python
```
"""
from __future__ import annotations

import abc
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

from plumbum import ProcessExecutionError

from benchbuild import command, signals, source
from benchbuild.settings import CFG
from benchbuild.utils import db, run
from benchbuild.utils.cmd import mkdir, rm, rmdir

LOG = logging.getLogger(__name__)

ReturnType = tp.TypeVar("ReturnType")
ReturnTypeA = tp.TypeVar("ReturnTypeA")
ReturnTypeB = tp.TypeVar("ReturnTypeB")
DecoratedFunction = tp.Callable[..., ReturnType]
FunctionDecorator = tp.Callable[[DecoratedFunction[ReturnTypeA]],
                                DecoratedFunction[ReturnTypeB]]

if tp.TYPE_CHECKING:
    import benchbuild.experiment.Experiment  # pylint: disable=unused-import
    import benchbuild.project.Project  # pylint: disable=unused-import
    import benchbuild.utils.schema.Experiment  # pylint: disable=unused-import


@enum.unique
class StepResult(enum.IntEnum):
    """Result type for action results."""

    UNSET = 0
    OK = 1
    CAN_CONTINUE = 2
    ERROR = 3


StepResultList = tp.List[StepResult]


def step_has_failed(
    result: StepResult,
    error_status: tp.Optional[tp.List[StepResult]] = None
) -> bool:
    if not error_status:
        error_status = [StepResult.ERROR, StepResult.CAN_CONTINUE]

    return result in error_status


def prepend_status(func: DecoratedFunction[str]) -> DecoratedFunction[str]:
    """Prepends the output of `func` with the status."""

    @tp.overload
    def wrapper(self: "Step", indent: int) -> str:
        ...

    @tp.overload
    def wrapper(self: "Step") -> str:
        ...

    @ft.wraps(func)
    def wrapper(self: "Step", *args: tp.Any, **kwargs: tp.Any) -> str:
        """Wrapper stub."""
        res = func(self, *args, **kwargs)
        if self.status is not StepResult.UNSET:
            res = f"[{self.status.name}]{res}"
        return res

    return wrapper


def log_before_after(name: str,
                     desc: str) -> FunctionDecorator[StepResult, StepResult]:
    """Log customized string before & after running func."""

    def func_decorator(
        func: DecoratedFunction[StepResult],
    ) -> DecoratedFunction[StepResult]:
        """Wrapper stub."""

        @ft.wraps(func)
        def wrapper(*args: tp.Any, **kwargs: tp.Any) -> StepResult:
            """Wrapper stub."""
            LOG.info("\n%s - %s", name, desc)
            res = func(*args, **kwargs)
            msg = f"{name} - {res.name}"
            if res != StepResult.ERROR:
                LOG.info(msg)
            else:
                LOG.error(msg)
            return res

        return wrapper

    return func_decorator


class Step:
    """
    Base class of a step.

    Raises:
        StopIteration: If we do not encapsulate more substeps.
    """

    NAME: tp.ClassVar[str] = ""
    DESCRIPTION: tp.ClassVar[str] = ""

    status: StepResult

    def __init_subclass__(cls, **kwargs: tp.Any):
        super().__init_subclass__(**kwargs)

        setattr(
            cls, "__call__",
            log_before_after(cls.NAME, cls.DESCRIPTION)(cls.__call__)
        )
        setattr(cls, "__str__", prepend_status(cls.__str__))

    def __init__(self, status: StepResult) -> None:
        self.status = status

    def __len__(self) -> int:
        return 1

    def __str__(self, indent: int = 0) -> str:
        return f"* Running action {self.NAME} - {self.DESCRIPTION}"

    def onerror(self) -> None:
        """
        Default implementation does nothing.
        """

    @abc.abstractmethod
    def __call__(self) -> StepResult:
        raise NotImplementedError


class ProjectStep(Step):
    """Base class of a project step.

    Adds a project attribute to the Step base class and some defaults.

    Raises:
        StopIteration: If we do not encapsulate more substeps.
    """

    NAME: tp.ClassVar[str] = ""
    DESCRIPTION: tp.ClassVar[str] = ""

    project: "benchbuild.project.Project"

    def __init__(self, project: "benchbuild.project.Project") -> None:
        super().__init__(StepResult.UNSET)
        self.project = project

    def __str__(self, indent: int = 0) -> str:
        return textwrap.indent("* Execute configured action.", indent * " ")

    def onerror(self) -> None:
        Clean(self.project)()

    @abc.abstractmethod
    def __call__(self) -> StepResult:
        raise NotImplementedError


StepTy_co = tp.TypeVar("StepTy_co", bound=Step, covariant=True)


class MultiStep(Step, tp.Generic[StepTy_co]):
    """Group multiple actions into one step.

    Usually used to define behavior on error, e.g., execute everything
    regardless of any errors, or fail everything upon first error.
    """

    NAME: tp.ClassVar[str] = ""
    DESCRIPTION: tp.ClassVar[str] = ""

    actions: tp.MutableSequence[StepTy_co]

    def __init__(
        self,
        actions: tp.Optional[tp.MutableSequence[StepTy_co]] = None
    ) -> None:
        super().__init__(StepResult.UNSET)

        self.actions = list(actions) if actions else []

    def __len__(self) -> int:
        return sum([len(x) for x in self.actions]) + 1

    def __iter__(self) -> tp.Iterator[StepTy_co]:
        return self.actions.__iter__()

    @abc.abstractmethod
    def __call__(self) -> StepResult:
        raise NotImplementedError

    def __str__(self, indent: int = 0) -> str:
        raise NotImplementedError

    def onerror(self) -> None:
        pass


class Clean(ProjectStep):
    NAME = "CLEAN"
    DESCRIPTION = "Cleans the build directory"

    def __init__(
        self,
        project: "benchbuild.project.Project",
        check_empty: bool = False
    ) -> None:
        super().__init__(project)
        self.check_empty = check_empty

    @staticmethod
    def clean_mountpoints(root: str) -> None:
        """Unmount any remaining mountpoints under :root.

        Args:
            root: All UnionFS-mountpoints under this directory will be
                  unmounted.
        """
        import psutil  # pylint: disable=import-outside-toplevel

        umount_paths = []
        real_root = os.path.realpath(root)
        for part in psutil.disk_partitions(all=True):
            if os.path.commonpath([part.mountpoint, real_root]) == real_root:
                if not part.fstype == "fuse.unionfs":
                    LOG.error("NON-UnionFS mountpoint found under %s", root)
                else:
                    umount_paths.append(part.mountpoint)

    def __call__(self) -> StepResult:
        if not CFG["clean"]:
            LOG.warning("Clean disabled by config.")
            return StepResult.OK
        if not self.project:
            LOG.warning("No object assigned to this action.")
            return StepResult.ERROR
        obj_builddir = os.path.abspath(self.project.builddir)
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
        project = self.project
        return textwrap.indent(
            f"* {project.name}: Clean the directory: {project.builddir}",
            indent * " "
        )


class MakeBuildDir(ProjectStep):
    NAME = "MKDIR"
    DESCRIPTION = "Create the build directory"

    def __call__(self) -> StepResult:
        if not self.project:
            return StepResult.ERROR
        if not os.path.exists(self.project.builddir):
            mkdir("-p", self.project.builddir)
        self.status = StepResult.OK
        return self.status

    def __str__(self, indent: int = 0) -> str:
        return textwrap.indent(
            f"* {self.project.name}: Create the build directory", indent * " "
        )


class Compile(ProjectStep):
    NAME = "COMPILE"
    DESCRIPTION = "Compile the project"

    def __call__(self) -> StepResult:
        try:
            self.project.compile()

        except ProcessExecutionError:
            self.status = StepResult.ERROR
            raise
        self.status = StepResult.OK

        return self.status

    def __str__(self, indent: int = 0) -> str:
        return textwrap.indent(f"* {self.project.name}: Compile", indent * " ")


class Run(ProjectStep):
    NAME = "RUN"
    DESCRIPTION = "Execute the run action"

    experiment: "benchbuild.experiment.Experiment"

    def __init__(
        self,
        project: "benchbuild.project.Project",
        experiment: "benchbuild.experiment.Experiment",
    ) -> None:
        super().__init__(project)

        self.experiment = experiment

    def __call__(self) -> StepResult:
        if CFG["db"]["enabled"]:
            group, session = run.begin_run_group(self.project, self.experiment)
            signals.handlers.register(run.fail_run_group, group, session)
        try:
            self.project.run_tests()
            if CFG["db"]["enabled"]:
                run.end_run_group(group, session)
            self.status = StepResult.OK
        except ProcessExecutionError:
            if CFG["db"]["enabled"]:
                run.fail_run_group(group, session)
            self.status = StepResult.ERROR
            raise
        except KeyboardInterrupt:
            if CFG["db"]["enabled"]:
                run.fail_run_group(group, session)
            self.status = StepResult.ERROR
            raise
        finally:
            if CFG["db"]["enabled"]:
                signals.handlers.deregister(run.fail_run_group)

        return self.status

    def __str__(self, indent: int = 0) -> str:
        return textwrap.indent(
            f"* {self.project.name}: Execute run-time tests.", indent * " "
        )


class Echo(Step):
    NAME = "ECHO"
    DESCRIPTION = "Print a message."

    message: str

    def __init__(self, message: str = "") -> None:
        super().__init__(StepResult.UNSET)
        self.message = message

    def __str__(self, indent: int = 0) -> str:
        return textwrap.indent(f"* echo: {self.message}", indent * " ")

    def __call__(self) -> StepResult:
        LOG.info(self.message)
        return StepResult.OK


def run_any_child(child: Step) -> StepResult:
    """Execute child step.

    Args:
        child: The child step.
    """
    return child()


class Any(MultiStep):
    NAME = "ANY"
    DESCRIPTION = "Just run all actions, no questions asked."

    def __call__(self) -> StepResult:
        length = len(self.actions)
        cnt = 0
        results = [StepResult.OK]
        for a in self.actions:
            cnt = cnt + 1
            result = a()
            results.append(result)

            if result == StepResult.ERROR:
                LOG.warning("%d actions left in queue", length - cnt)

        self.status = StepResult.OK
        if StepResult.ERROR in results:
            self.status = StepResult.CAN_CONTINUE
        return self.status

    def __str__(self, indent: int = 0) -> str:
        sub_actns = "\n".join([a.__str__(indent + 1) for a in self.actions])
        return textwrap.indent("* Execute all of:\n" + sub_actns, indent * " ")


class Experiment(Any):
    NAME = "EXPERIMENT"
    DESCRIPTION = "Run a experiment, wrapped in a db transaction"

    experiment: "benchbuild.experiment.Experiment"

    def __init__(
        self,
        experiment: "benchbuild.experiment.Experiment",
        actions: tp.Optional[tp.MutableSequence[Step]],
    ) -> None:
        _actions: tp.MutableSequence[Step] = [
            Echo(message=f"Start experiment: {experiment.name}")
        ]
        _actions.extend(actions if actions else [])
        _actions.extend([
            Echo(message=f"Completed experiment: {experiment.name}")
        ])

        super().__init__(_actions)
        self.experiment = experiment

    def begin_transaction(
        self,
    ) -> tp.Tuple["benchbuild.utils.schema.Experiment", tp.Any]:
        import sqlalchemy as sa  # pylint: disable=import-outside-toplevel
        experiment, session = db.persist_experiment(self.experiment)
        if experiment.begin is None:
            experiment.begin = datetime.now()
            experiment.end = experiment.begin
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
    def end_transaction(
        experiment: "benchbuild.utils.schema.Experiment", session: tp.Any
    ) -> None:
        import sqlalchemy as sa  # pylint: disable=import-outside-toplevel
        try:
            experiment.end = max(experiment.end, datetime.now())
            session.add(experiment)
            session.commit()
        except sa.exc.InvalidRequestError as inv_req:
            LOG.error(inv_req)

    def __run_children(self, num_processes: int) -> tp.List[StepResult]:
        # pylint: disable=import-outside-toplevel
        import pathos.multiprocessing as mp

        results = []
        actions = self.actions

        try:
            with mp.Pool(num_processes) as pool:
                results = pool.map(run_any_child, actions)
        except KeyboardInterrupt:
            LOG.info("Experiment aborting by user request")
            results.append(StepResult.ERROR)
        except Exception:
            LOG.error("Experiment terminates "
                      "because we got an exception:")
            e_type, e_value, e_traceb = sys.exc_info()
            lines = traceback.format_exception(e_type, e_value, e_traceb)
            LOG.error("".join(lines))
            results.append(StepResult.ERROR)
        return results

    def __call__(self) -> StepResult:
        results = []
        session = None
        if CFG["db"]["enabled"]:
            experiment, session = self.begin_transaction()
        try:
            results = self.__run_children(int(CFG["parallel_processes"]))
        finally:
            if CFG["db"]["enabled"]:
                self.end_transaction(experiment, session)
                signals.handlers.deregister(self.end_transaction)
        self.status = max(results) if results else StepResult.OK
        return self.status

    def __str__(self, indent: int = 0) -> str:
        sub_actns = "\n".join([a.__str__(indent + 1) for a in self.actions])
        return textwrap.indent(
            f"\nExperiment: {self.experiment.name}\n{sub_actns}", indent * " "
        )


class RequireAll(MultiStep):
    NAME = "REQUIRE ALL"
    DESCRIPTION = "All child steps need to succeed"

    def __call__(self) -> StepResult:
        results: tp.List[StepResult] = []

        total_steps = len(self.actions)

        def no_fail(*args: tp.Any, **kwargs: tp.Any):
            return StepResult.ERROR not in results

        for i, action in itertools.takewhile(no_fail, enumerate(self.actions)):
            result = StepResult.UNSET
            try:
                result = action()
            except ProcessExecutionError as proc_ex:
                LOG.error("\n==== ERROR ====")
                LOG.error(
                    "Execution of a binary failed in step: %s", str(action)
                )
                LOG.error(str(proc_ex))
                LOG.error("==== ERROR ====\n")
                result = StepResult.ERROR
            except KeyboardInterrupt:
                LOG.info("User requested termination.")
                action.onerror()
                action.status = StepResult.ERROR
                raise
            except Exception:
                LOG.error(
                    "Exception in step #%d/%d: %s",
                    i,
                    total_steps,
                    str(action),
                    exc_info=sys.exc_info(),
                )
                result = StepResult.ERROR

            results.append(result)
            action.status = result
            is_failed = StepResult.ERROR in results
            if is_failed:
                LOG.error("Execution of: '%s' failed.", str(action))
                LOG.error("'%s' cannot continue.", str(self))
                action.onerror()

        self.status = max(results) if results else StepResult.UNSET
        return self.status

    def __str__(self, indent: int = 0) -> str:
        sub_actns = "\n".join([a.__str__(indent + 1) for a in self.actions])
        return textwrap.indent(f"* All required:\n{sub_actns}", indent * " ")


WorkloadTy = tp.Callable[[], tp.Any]


class RunWorkload(ProjectStep):
    NAME = "RUN WORKLOAD"
    DESCRIPTION = "Run a project's workload"

    _workload: tp.Optional[WorkloadTy]

    @property
    def workload_ref(self) -> WorkloadTy:
        # Workaround for MyPy...
        assert self._workload is not None, "non-optional optional triggered"
        return self._workload

    def __init__(
        self,
        project: "benchbuild.project.Project",
        workload: tp.Optional[WorkloadTy] = None
    ) -> None:
        super().__init__(project)

        self._workload = workload

    def __call__(self) -> StepResult:
        try:
            self.workload_ref()
            self.status = StepResult.OK
        except ProcessExecutionError:
            self.status = StepResult.ERROR
            raise
        except KeyboardInterrupt:
            self.status = StepResult.ERROR
            raise
        return self.status

    def __str__(self, indent: int = 0) -> str:
        return textwrap.indent(f"* Run: {str(self.workload_ref)}", indent * " ")


class RunWorkloads(MultiStep):
    NAME = "RUN WORKLOADS"
    DESCRIPTION = "Generic run all project workloads"

    project: "benchbuild.project.Project"
    experiment: "benchbuild.experiment.Experiment"

    def __init__(
        self,
        project: "benchbuild.project.Project",
        experiment: "benchbuild.experiment.Experiment",
        run_only: tp.Optional[command.WorkloadSet] = None,
    ) -> None:
        super().__init__()

        self.project = project
        self.experiment = experiment

        index = command.unwrap(project.workloads, project)
        workloads = itertools.chain(
            *command.filter_workload_index(run_only, index)
        )

        for workload in workloads:
            self.actions.extend([
                RunWorkload(project, command.ProjectCommand(project, workload))
            ])

    def __call__(self) -> StepResult:
        if CFG["db"]["enabled"]:
            group, session = run.begin_run_group(self.project, self.experiment)
            signals.handlers.register(run.fail_run_group, group, session)
        try:
            self.status = max([workload() for workload in self.actions],
                              default=StepResult.OK)
            if CFG["db"]["enabled"]:
                run.end_run_group(group, session)
        except ProcessExecutionError:
            if CFG["db"]["enabled"]:
                run.fail_run_group(group, session)
            self.status = StepResult.ERROR
            raise
        except KeyboardInterrupt:
            if CFG["db"]["enabled"]:
                run.fail_run_group(group, session)
            self.status = StepResult.ERROR
            raise
        finally:
            if CFG["db"]["enabled"]:
                signals.handlers.deregister(run.fail_run_group)

        return self.status

    def __str__(self, indent: int = 0) -> str:
        sub_actns = "\n".join([a.__str__(indent + 1) for a in self.actions])
        return textwrap.indent(
            f"* Require all of {self.project.name}'s workloads:\n{sub_actns}",
            indent * " "
        )


class CleanExtra(Step):
    NAME = "CLEAN EXTRA"
    DESCRIPTION = "Cleans the extra directories."

    def __init__(self) -> None:
        super().__init__(StepResult.UNSET)

    def __call__(self) -> StepResult:
        if not CFG["clean"]:
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
                textwrap.indent(f"* Clean the directory: {p}", indent * " ")
            )
        return "\n".join(lines)


class ProjectEnvironment(ProjectStep):
    NAME = "ENV"
    DESCRIPTION = "Prepare the project environment."

    def __call__(self) -> StepResult:
        project = self.project
        project.clear_paths()

        revision = project.revision

        for variant in revision.variants:
            name = variant.name()
            LOG.info("Fetching %s @ %s", str(name), variant.version)
            src = variant.source()
            src.version(project.builddir, str(variant))

        self.status = StepResult.OK
        return self.status

    def __str__(self, indent: int = 0) -> str:
        project = self.project
        revision = project.revision
        version_str = str(revision)

        return textwrap.indent(
            f"* Project environment for: {project.name} @ {version_str}",
            indent * " "
        )


class SetProjectVersion(ProjectStep):
    NAME = "SET PROJECT VERSION"
    DESCRIPTION = "Checkout a project version"

    revision: source.Revision

    def __init__(
        self,
        project: "benchbuild.project.Project",
        *revision_strings: source.base.RevisionStr,
    ) -> None:
        super().__init__(project)

        self.revision = source.revision_from_str(
            revision_strings, type(project)
        )

    def __call__(self) -> StepResult:
        project = self.project
        revision = project.active_revision
        revision.update(self.revision)

        for variant in revision.variants:
            name = variant.name()
            LOG.info("Fetching %s @ %s", str(name), variant.version)
            src = variant.source()
            src.version(project.builddir, str(variant))

        project.active_revision = revision
        self.status = StepResult.OK
        return self.status

    def __str__(self, indent: int = 0) -> str:
        project = self.project
        version_str = str(self.revision)

        return textwrap.indent(
            f"* Add project version {version_str} for: {project.name}",
            indent * " "
        )
