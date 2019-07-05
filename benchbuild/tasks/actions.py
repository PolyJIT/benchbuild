"""New actions implementation."""
import itertools
import logging
import os
import textwrap
from abc import abstractmethod
from contextlib import ExitStack, contextmanager
from datetime import datetime
from typing import Iterable, List, Callable, Union, Any, Optional

import attr
import sqlalchemy as sa
from plumbum import ProcessExecutionError

from benchbuild import signals
from benchbuild.project import Project
from benchbuild.experiment import Experiment
from benchbuild.utils.schema import Experiment as db_exp_t
from benchbuild.settings import CFG
from benchbuild.utils import db
from benchbuild.utils.actions import StepResult
from benchbuild.utils.cmd import mkdir, rm, rmdir

LOG = logging.getLogger(__name__)

RunnableTask = Union['Task', 'TaskGroup', 'TaskManager']
ChildTasks = Iterable[RunnableTask]


@attr.s(auto_attribs=True)
class TaskPolicy:
    """
    Event class interface for task policies.

    This implements two event types and a continuation condition for tasks.
    Policies control the behavior of a task group when there is an error
    or a new result. Furthermore, we control the execution process by
    providing the result for the can_continue predicate.

    Concrete implementations provided include the Fail and Continue policy.

    Subclasses _must_ implement at least the can_continue method.
    """
    state: StepResult = StepResult.OK

    def on_error(self, task_result: StepResult, exception=None):
        """What do we do with an error."""

    def on_result(self, task_result: StepResult):
        """What do we do with a result."""

    @abstractmethod
    def can_continue(self, task_result: StepResult) -> bool:
        """Can execution of multiple child steps continue?"""


@attr.s(auto_attribs=True)
class TaskGroup:
    """
    A warpper class with metadata for a group of Tasks.

    Attributes:
        name: the name of the task.
        description: a description for this task.
        children: the tasks that are grouped together.
        policy: the policy we implement for the task group,
                in case of errors during execution.
    """
    name: str
    description: str
    children: ChildTasks
    policy: TaskPolicy

    def __attrs_post_init__(self):
        for child in self.children:
            if isinstance(child, Task):
                child.owner = self

    def on_error(self, task_result: StepResult, exception=None):
        """What do we do with an error."""
        return self.policy.on_error(task_result, exception)

    def on_result(self, task_result: StepResult):
        """What do we do with a result."""
        return self.policy.on_result(task_result)

    def can_continue(self, task_result: StepResult) -> bool:
        """Can execution of multiple child steps continue?"""
        return self.policy.can_continue(task_result)

    def tasks(self):
        all_tasks = [
            child.tasks() if hasattr(child, 'tasks') else [child]
            for child in self.children
        ]
        return list(itertools.chain(*all_tasks))

    def __str__(self, indent=0):
        ret_str = __print_ident__(self.name, self.description, indent)
        ret_str += "\n"
        ret_str += "\n".join(
            [child.__str__(indent=indent + 1) for child in self.children])
        return ret_str


@attr.s(auto_attribs=True)
class Task:
    """
    A wrapper class with metadata for callables.

    Attributes:
        name: the name of the task.
        description: a description for this task.
        call: the function that we delegate a __call__ to.
        owner: the optional owner of this task, used for policies.
    """
    name: str
    description: str
    call: Callable[[], StepResult]
    owner: Optional[TaskGroup] = None

    def __call__(self) -> StepResult:
        """Perform actions that define this step implementation."""
        delegate_fn = self.call
        return delegate_fn()

    def can_continue(self, task_result: StepResult) -> bool:
        """Can execution of multiple child steps continue?"""
        if self.owner:
            return self.owner.can_continue(task_result)
        else:
            return True

    def __str__(self, indent=0):
        return __print_ident__(self.name, self.description, indent)


@attr.s
class Fail(TaskPolicy):
    """Task policy that always fails on first error."""
    def can_continue(self, task_result: StepResult) -> bool:
        res = task_result in [StepResult.OK, StepResult.CAN_CONTINUE]
        if not res:
            self.state = task_result

        return self.state in [StepResult.OK, StepResult.CAN_CONTINUE]


@attr.s
class Continue(TaskPolicy):
    """Task policy that always continues."""

    def can_continue(self, task_result: StepResult) -> bool:
        self.state = task_result
        return True


def __print_ident__(name: str, description: str, indent: int = 0) -> str:
    return textwrap.indent(
        "* {name}: {desc}".format(name=name, desc=description), indent * ' ')


def catch_exceptions(task: 'Task'):
    try:
        result = task()
    except (ProcessExecutionError, KeyboardInterrupt, OSError) as ex:
        if task.owner:
            task.owner.on_error(result, ex)
        result = StepResult.ERROR

    return result


@contextmanager
def per_task_context(context, task: Task):
    with ExitStack() as stack:
        for mgr in context:
            stack.enter_context(mgr(task))
        yield task


@contextmanager
def global_context(context):
    with ExitStack() as stack:
        for mgr in context:
            stack.enter_context(mgr)
        yield


def __merge_results__(results: List[StepResult],
                      merge_results: Union[Iterable[StepResult], StepResult]
                      ) -> Iterable[StepResult]:
    if isinstance(merge_results, Iterable):
        return list(itertools.chain(results, merge_results))

    new_results: List[StepResult] = results
    new_results.append(merge_results)

    return new_results


@attr.s(auto_attribs=True)
class TaskManager:
    name: str
    description: str

    plan: TaskGroup
    task_context: Iterable[Any] = attr.Factory(list)
    global_context: Iterable[Any] = attr.Factory(list)

    def run(self):
        res = StepResult.OK
        results = []

        with global_context(self.global_context):
            for task in self.plan.tasks():
                if task.can_continue(res):
                    with per_task_context(self.task_context,
                                          task) as task_context:
                        res = task_context()
                results = __merge_results__(results, res)
        return results

    def tasks(self):
        all_tasks = [
            child.tasks() for child in self.plan if hasattr(child, 'tasks')
        ]
        return list(itertools.chain(*all_tasks))

    def __call__(self) -> Iterable[StepResult]:
        return self.run()

    def __str__(self, indent=0):
        return self.plan.__str__(indent=indent)


def fail_group(*tasks: RunnableTask) -> TaskGroup:
    """
    Create a group of tasks that fails on first error.

    Args:
        *tasks: Any number of runnable tasks.

    Returns:
        a task group.
    """
    return TaskGroup("fail", "Fail on first error", tasks, Fail())


def continue_group(*tasks: RunnableTask) -> TaskGroup:
    """
    Create a group of tasks that always continues.

    Args:
        *tasks: Any number of runnable tasks.

    Returns:
        a task group.
    """
    return TaskGroup("continue", "Continue on any error", tasks, Continue())


def echo(message: str) -> Task:
    """Print a message."""

    def call_impl() -> StepResult:
        LOG.info(message)
        return StepResult.OK

    return Task("Echo", message, call_impl)


def run_project(project: Project) -> Task:
    """Run a project."""
    return Task("run", "Run a project", lambda: project.run())


def compile_project(project: Project) -> Task:
    """Compile the project."""
    return Task("compile", "Compile a project", lambda: project.compile())


def make_builddir(project: Project) -> Task:
    """Create the build directory."""

    def call_impl() -> StepResult:
        if not os.path.exists(project.builddir):
            mkdir("-p", project.builddir)
        return StepResult.OK

    return Task("mkdir", "create the build directory", call_impl)


def clean_extra() -> Task:
    """Cleans the extra directories."""

    def call_impl() -> StepResult:
        if not CFG['clean']:
            return StepResult.OK

        paths = CFG["cleanup_paths"].value
        for p in paths:
            if os.path.exists(p):
                rm("-r", p)
        return StepResult.OK

    return Task("clean extra", "clean all external directories", call_impl)


def __clean_mountpoints__(root: str):
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


def clean(project: Project, check_empty: bool = False) -> Task:
    """Clean the build directory."""

    def call_impl():
        if not CFG['clean']:
            LOG.warning("Clean disabled by config.")
            return StepResult.CAN_CONTINUE
        obj_builddir = os.path.abspath(project.builddir)
        if os.path.exists(obj_builddir):
            LOG.debug("Path %s exists", obj_builddir)
            __clean_mountpoints__(obj_builddir)
            if check_empty:
                rmdir(obj_builddir, retcode=None)
            else:
                rm("-rf", obj_builddir)
        else:
            LOG.debug("Path %s did not exist anymore", obj_builddir)
        return StepResult.OK

    return Task("clean", "clean the build directory.", call_impl)


def __begin_experiment__(exp: Experiment):
    db_exp, session = db.persist_experiment(exp)
    if db_exp.begin is None:
        db_exp.begin = datetime.now()
    else:
        db_exp.begin = min(db_exp.begin, datetime.now())
    session.add(db_exp)
    try:
        session.commit()
    except sa.orm.exc.StaleDataError:
        LOG.error("Transaction isolation level caused a StaleDataError")

    # React to external signals
    signals.handlers.register(__end_experiment__, db_exp, session)

    return db_exp, session


def __end_experiment__(db_exp: db_exp_t, session: sa.orm.session.Session):
    try:
        if db_exp.end is None:
            db_exp.end = datetime.now()
        else:
            db_exp.end = max(db_exp.end, datetime.now())
        session.add(db_exp)
        session.commit()
    except sa.exc.InvalidRequestError as inv_req:
        LOG.error(inv_req)


def manage_experiment(experiment: Experiment, tasks: TaskGroup) -> TaskManager:
    """Run an experiment, wrapped in a db transaction."""
    name: str = experiment.name
    exp_tasks: ChildTasks = [
        echo("Start experiment: {}".format(name)), tasks,
        echo("Completed experiment: {}".format(name))
    ]

    task_group: TaskGroup = continue_group(*exp_tasks)
    task_manager = TaskManager(
        name="experiment",
        description="run an experiment",
        plan=task_group,
        task_context=[LogTasks],
        global_context=[ExperimentTransaction(experiment)])

    return task_manager


@attr.s(auto_attribs=True)
class ExperimentTransaction:
    experiment: Experiment

    db_exp: db_exp_t = attr.ib(default=None)
    db_session: sa.orm.session.Session = attr.ib(default=None)

    def __enter__(self):
        self.db_exp, self.db_session = __begin_experiment__(self.experiment)

    def __exit__(self, type, value, traceback):
        __end_experiment__(self.db_exp, self.db_session)
        return False


@attr.s(auto_attribs=True)
class LogTasks:
    task: Task

    def __enter__(self):
        LOG.warning("\n%s - %s", self.task.name, self.task.description)

    def __exit__(self, type, value, traceback):
        LOG.warning("%s COMPLETE", self.task.name)
        return False
