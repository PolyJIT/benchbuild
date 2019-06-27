"""New actions implementation."""
import itertools
import logging
import os
import textwrap
from abc import abstractmethod
from contextlib import AbstractContextManager, ExitStack, contextmanager
from datetime import datetime
from typing import Iterable, List, Union

import attr
import sqlalchemy as sa
from plumbum import ProcessExecutionError

from benchbuild import signals
from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils import db
from benchbuild.utils.actions import StepResult
from benchbuild.utils.cmd import mkdir, rm, rmdir

LOG = logging.getLogger(__name__)

@attr.s
class NamedTaskEntity:
    def __attrs_post_init__(self):
        self.name: str = type(self).__name__
        self.description: str = type(self).__doc__

@attr.s
class GroupPolicy(NamedTaskEntity):
    children: List[Union['GroupPolicy', 'Task']] = attr.ib()
    state: StepResult = attr.ib(kw_only=True, default=StepResult.OK)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

        for child in self.children:
            child.owner = self

    @abstractmethod
    def can_continue(self, task_result: StepResult) -> bool:
        ...

    def tasks(self):
        all_tasks = [child.tasks() for child in self.children]
        return list(itertools.chain(*all_tasks))

    def __str__(self, indent=0) -> str:
        ret_str = textwrap.indent(
            "* {name}: {desc}\n".format(name=self.name, desc=self.description),
            indent * ' ')
        ret_str += "\n".join([
            textwrap.indent(child.__str__(indent=indent + 1), indent * " ")
            for child in self.children
        ])
        return ret_str


@attr.s
class FailOnError(GroupPolicy):
    def can_continue(self, task_result: StepResult) -> bool:
        res = task_result in [StepResult.OK, StepResult.CAN_CONTINUE]
        if not res:
            self.state = task_result

        return self.state in [StepResult.OK, StepResult.CAN_CONTINUE]


@attr.s
class ContinueOnError(GroupPolicy):
    def can_continue(self, task_result: StepResult) -> bool:
        self.state = task_result
        return True

@attr.s
class Task(NamedTaskEntity):
    def __attrs_post_init__(self):
        super().__attrs_post_init__()

        self.owner: 'GroupPolicy' = None

    def catch_exceptions(self, task: 'Task') -> StepResult:
        try:
            result = task()
        except (ProcessExecutionError, KeyboardInterrupt, OSError) as ex:
            task.on_error(result, ex)
            result = StepResult.ERROR

        return result

    @abstractmethod
    def on_error(self, task_result: StepResult, exception=None):
        """What do we do with an error."""

    @abstractmethod
    def on_result(self, task_result: StepResult):
        """What do we do with a result."""

    def can_continue(self, task_result: StepResult) -> bool:
        """Can execution of multiple child steps continue?"""
        if self.owner:
            return self.owner.can_continue(task_result)
        return True

    def tasks(self) -> List[Union['Task', GroupPolicy]]:
        return [self]

    def __call__(self) -> StepResult:
        """Perform actions that define this step implementation."""

    def __str__(self, indent=0):
        return textwrap.indent(
            "* {name}: {desc}".format(name=self.name, desc=self.description),
            indent * ' ')


@attr.s
class Echo(Task):
    """Print a message."""
    message: str = attr.ib(kw_only=True)

    def __call__(self) -> StepResult:
        LOG.info(self.message)
        return StepResult.OK

    def __str__(self, indent=0):
        return textwrap.indent(self.message, indent * ' ')


@attr.s
class Run(Task):
    """Run a project."""
    project: Project = attr.ib()

    def __call__(self) -> StepResult:
        result = self.project.run()
        return result

@attr.s
class Compile(Task):
    """Compile the project."""
    project: Project = attr.ib()

    def __call__(self) -> StepResult:
        result = self.project.compile()
        return result

@attr.s
class MakeBuildDir(Task):
    """Create the build directory."""
    project: Project = attr.ib()

    def __call__(self) -> StepResult:
        if not os.path.exists(self.project.builddir):
            mkdir("-p", self.project.builddir)
        return StepResult.OK

@attr.s
class Clean(Task):
    """Clean the build directory."""
    project: Project = attr.ib()
    check_empty: bool = attr.ib(default=False)

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

    def __call__(self) -> StepResult:
        if not CFG['clean']:
            LOG.warning("Clean disabled by config.")
            return StepResult.CAN_CONTINUE
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
        return StepResult.OK

@attr.s
class CleanExtra(Task):
    """Cleans the extra directories."""
    def __call__(self) -> StepResult:
        if not CFG['clean']:
            return StepResult.OK

        paths = CFG["cleanup_paths"].value
        for p in paths:
            if os.path.exists(p):
                rm("-r", p)
        return StepResult.OK



@attr.s
class TaskManager(NamedTaskEntity):
    plan: Union['GroupPolicy', 'Task'] = attr.ib()

    def __merge_results__(self, results, merge_results):
        if isinstance(merge_results, Iterable):
            return list(itertools.chain(results, merge_results))

        new_results = results
        new_results.append(merge_results)
        return new_results

    def run(self):
        res = StepResult.OK
        results = []
        for task in self.plan.tasks():
            if task.can_continue(res):
                with self.execution_context(task) as task_context:
                    res = task_context()

            results = self.__merge_results__(results, res)
        return results

    @contextmanager
    def execution_context(self, task: Task):
        log_ctx = LogTasks(task)

        mgrs = [
            log_ctx
        ]

        with ExitStack() as stack:
            for mgr in mgrs:
                stack.enter_context(mgr)
            yield task

    def __str__(self, indent=0):
        ret_str = textwrap.indent(
            "* {name}: {desc}\n".format(name=self.name,
                                        desc=self.description), indent * ' ')
        ret_str += self.plan.__str__(indent=indent+1)
        return ret_str

@attr.s
class Experiment(TaskManager, Task):
    """Run an experiment, wrapped in a db transaction."""
    experiment = attr.ib()

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        name = self.experiment.name
        self.plan = FailOnError([
            Echo(message="Start experiment: {0}".format(name)),
            self.plan,
            Echo(message="Completed experiment: {0}".format(name))
        ])


    def begin_transaction(self):
        experiment, session = db.persist_experiment(self.experiment)
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

    @contextmanager
    def execution_context(self, task: Task) -> List[AbstractContextManager]:
        experiment, session = self.begin_transaction()
        yield task
        self.end_transaction(experiment, session)

    def __call__(self) -> StepResult:
        results = self.run()
        return results


@attr.s
class LogTasks(AbstractContextManager):
    task: Task = attr.ib()

    def __enter__(self):
        LOG.info("\n%s - %s", self.task.name, self.task.description)

    def __exit__(self, type, value, traceback):
        LOG.info("%s COMPLETE")
