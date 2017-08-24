"""
This defines classes that can be used to implement a series of Actions.
"""
import abc
from datetime import datetime
import enum
import functools as ft
import logging
import os
import sys
import textwrap
import traceback

import benchbuild.signals as signals
from benchbuild.settings import CFG
from benchbuild.utils.db import persist_experiment

from benchbuild.utils.cmd import mkdir, rm, rmdir
from plumbum import ProcessExecutionError


LOG = logging.getLogger(__name__)


@enum.unique
class StepResult(enum.IntEnum):
    UNSET = 0,
    OK = 1,
    CAN_CONTINUE = 2
    ERROR = 3,




def to_step_result(f):
    @ft.wraps(f)
    def wrapper(*args, **kwargs):
        res = f(*args, **kwargs)
        if not res:
            res = [StepResult.OK]

        if not hasattr(res, "__iter__"):
            res = [res]
        return res

    return wrapper


def prepend_status(f):
    @ft.wraps(f)
    def wrapper(self, *args, **kwargs):
        res = f(self, *args, **kwargs)
        if self.status is not StepResult.UNSET:
            res = "[{status}]".format(status=self.status.name) + res
        return res
    return wrapper

def notify_step_begin_end(f):
    @ft.wraps(f)
    def wrapper(self, *args, **kwargs):
        cls = self.__class__
        on_step_begin = cls.ON_STEP_BEGIN
        on_step_end = cls.ON_STEP_END

        for begin_listener in on_step_begin:
            begin_listener(self)

        res =  f(self, *args, **kwargs)

        for end_listener in on_step_end:
            end_listener(self, f)
        return res
    return wrapper




def log_before_after(name, desc):
    def func_decorator(f):
        @ft.wraps(f)
        def wrapper(*args, **kwargs):
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
    def __new__(metacls, name, bases, namespace, **kwds):
        result = abc.ABCMeta.__new__(metacls, name, bases, dict(namespace))

        NAME = result.NAME
        DESCRIPTION = result.DESCRIPTION
        if NAME and DESCRIPTION:
            result.__call__ = log_before_after(
                NAME, DESCRIPTION)(to_step_result(result.__call__))
        else:
            result.__call__ = to_step_result(result.__call__)

        result.__str__ = prepend_status(result.__str__)
        return result


class Step(metaclass=StepClass):
    NAME = None
    DESCRIPTION = None

    ON_STEP_BEGIN = []
    ON_STEP_END = []

    def __init__(self, project_or_experiment, action_fn=None):
        self._obj = project_or_experiment
        self._action_fn = action_fn
        self._status = StepResult.UNSET

    def __len__(self):
        return 1

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    @notify_step_begin_end
    def __call__(self):
        if not self._action_fn:
            return StepResult.ERROR
        self._action_fn()
        self.status = StepResult.OK
        return StepResult.OK

    def __str__(self, indent=0):
        return textwrap.indent(
            "* {name}: Execute configured action.".format(
                    name=self._obj.name), indent * " ")

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    def onerror(self):
        Clean(self._obj)()


class Clean(Step):
    NAME = "CLEAN"
    DESCRIPTION = "Cleans the build directory"

    def __init__(self, project_or_experiment,
                 action_fn=None, check_empty=False):
        super(Clean, self).__init__(project_or_experiment, action_fn)
        self.check_empty = check_empty

    def __clean_mountpoints__(self, root):
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
        if not CFG['clean'].value():
            LOG.warn("Clean disabled by config.")
            return
        if not self._obj:
            LOG.warn("No object assigned to this action.")
            return
        obj_builddir = os.path.abspath(self._obj.builddir)
        if os.path.exists(obj_builddir):
            LOG.debug("Path %s exists", obj_builddir)
            self.__clean_mountpoints__(obj_builddir)
            if self.check_empty:
                rmdir(obj_builddir, retcode=None)
            else:
                rm("-rf", obj_builddir)
        else:
            LOG.debug("Path %s did not exist anymore", obj_builddir)
        self.status = StepResult.OK

    def __str__(self, indent=0):
        return textwrap.indent("* {0}: Clean the directory: {1}".format(
            self._obj.name, self._obj.builddir), indent * " ")


class MakeBuildDir(Step):
    NAME = "MKDIR"
    DESCRIPTION = "Create the build directory"

    @notify_step_begin_end
    def __call__(self):
        if not self._obj:
            return
        if not os.path.exists(self._obj.builddir):
            mkdir("-p", self._obj.builddir)
        self.status = StepResult.OK

    def __str__(self, indent=0):
        return textwrap.indent(
            "* {0}: Create the build directory".format(self._obj.name),
            indent * " ")


class Prepare(Step):
    NAME = "PREPARE"
    DESCRIPTION = "Prepare project build folder"

    def __init__(self, project):
        super(Prepare, self).__init__(project, project.prepare)

    def __str__(self, indent=0):
        return textwrap.indent("* {0}: Prepare".format(self._obj.name),
                               indent * " ")


class Download(Step):
    NAME = "DOWNLOAD"
    DESCRIPTION = "Download project source files"

    def __init__(self, project):
        super(Download, self).__init__(project, project.download)

    def __str__(self, indent=0):
        return textwrap.indent("* {0}: Download".format(self._obj.name),
                               indent * " ")


class Configure(Step):
    NAME = "CONFIGURE"
    DESCRIPTION = "Configure project source files"

    def __init__(self, project):
        super(Configure, self).__init__(project, project.configure)

    def __str__(self, indent=0):
        return textwrap.indent("* {0}: Configure".format(self._obj.name),
                               indent * " ")


class Build(Step):
    NAME = "BUILD"
    DESCRIPTION = "Build the project"

    def __init__(self, project):
        super(Build, self).__init__(project, project.build)

    def __str__(self, indent=0):
        return textwrap.indent("* {0}: Compile".format(self._obj.name),
                               indent * " ")


class Run(Step):
    NAME = "RUN"
    DESCRIPTION = "Execute the run action"

    def __init__(self, project):
        action_fn = ft.partial(project.run, project.runtime_extension)
        super(Run, self).__init__(project, action_fn)

    @notify_step_begin_end
    def __call__(self):
        if not self._obj:
            return
        if not self._action_fn:
            return

        self._action_fn()
        self.status = StepResult.OK

    def __str__(self, indent=0):
        return textwrap.indent(
            "* {0}: Execute run-time tests.".format(self._obj.name),
            indent * " ")


class Echo(Step):
    NAME = 'ECHO'
    DESCRIPTION = 'Print a message.'

    def __init__(self, message):
        self._message = message
        self._status = StepResult.UNSET

    def __str__(self, indent=0):
        return textwrap.indent("* echo: {0}".format(self._message),
                               indent * " ")

    @notify_step_begin_end
    def __call__(self):
        LOG.info(self._message)


class Any(Step):
    NAME = "ANY"
    DESCRIPTION = "Just run all actions, no questions asked."

    def __init__(self, actions):
        self._actions = actions
        super(Any, self).__init__(None, None)

    def __len__(self):
        return sum([len(x) for x in self._actions]) + 1

    def __iter__(self):
        return self._actions.__iter__()

    @notify_step_begin_end
    def __call__(self):
        length = len(self._actions)
        cnt = 0
        results = [StepResult.OK]
        for a in self._actions:
            cnt = cnt + 1
            result = a()
            results.append(result)

            if StepResult.ERROR in result:
                LOG.warning("%d actions left in queue", length - cnt)
        self.status = StepResult.OK
        if StepResult.EROR in results:
            self.status = StepResult.CAN_CONTINUE

    def __str__(self, indent=0):
        sub_actns = [a.__str__(indent + 1) for a in self._actions]
        sub_actns = "\n".join(sub_actns)
        return textwrap.indent("* Execute all of:\n" + sub_actns, indent * " ")


class Experiment(Any):
    NAME = "EXPERIMENT"
    DESCRIPTION = "Run a experiment, wrapped in a db transaction"

    def __init__(self, experiment, actions):
        self._experiment = experiment
        actions = \
            [Echo("Start experiment: {0}".format(experiment.name))] + \
            actions + \
            [Echo("Completed experiment: {0}".format(experiment.name))]
        super(Experiment, self).__init__(actions)

    def begin_transaction(self):
        experiment, session = persist_experiment(self._experiment)
        if experiment.begin is None:
            experiment.begin = datetime.now()
        else:
            experiment.begin = min(experiment.begin, datetime.now())
        session.add(experiment)
        session.commit()

        # React to external signals
        signals.handlers.register(self.end_transaction, experiment, session)

        return experiment, session

    def end_transaction(self, experiment, session):
        if experiment.end is None:
            experiment.end = datetime.now()
        else:
            experiment.end = max(experiment.end, datetime.now())
        session.add(experiment)
        session.commit()

    @notify_step_begin_end
    def __call__(self):
        results = []
        experiment = None
        session = None
        try:
            res = self.begin_transaction()
            experiment = res[0]
            session = res[1]
            for a in self._actions:
                try:
                    result = a()
                    results.extend(result)
                except KeyboardInterrupt:
                    LOG.info("Experiment aborting by user request")
                    results.append(StepResult.ERROR)
                    break
                except Exception:
                    LOG.error("Experiment terminates "
                              "because we got an exception:")
                    e_type, e_value, e_traceb = sys.exc_info()
                    lines = traceback.format_exception(
                        e_type, e_value, e_traceb)
                    results.append(StepResult.ERROR)
                    LOG.error("".join(lines))
                    break
        finally:
            self.end_transaction(experiment, session)
            signals.handlers.deregister(self.end_transaction,
                                        experiment, session)
        self.status = max(results)
        return results

    def __str__(self, indent=0):
        sub_actns = [a.__str__(indent + 1) for a in self._actions]
        sub_actns = "\n".join(sub_actns)
        return textwrap.indent(
            "\nExperiment: {0}\n".format(self._experiment.name) + sub_actns,
            indent * " ")


class RequireAll(Step):
    def __init__(self, actions):
        self._actions = actions
        super(RequireAll, self).__init__(None, None)

    def __len__(self):
        return sum([len(x) for x in self._actions]) + 1

    def __iter__(self):
        return self._actions.__iter__()

    @notify_step_begin_end
    def __call__(self):
        results = []
        for i, action in enumerate(self._actions):
            try:
                results.extend(action())
            except ProcessExecutionError as proc_ex:
                LOG.error("\n==== ERROR ====")
                LOG.error(
                    "Execution of a binary failed in step: %s", str(action))
                LOG.error(str(proc_ex))
                LOG.error("==== ERROR ====\n")
                results.append(StepResult.ERROR)
            except KeyboardInterrupt:
                LOG.info("User requested termination.")
                action.onerror()
                results.append(StepResult.ERROR)
                raise
            except (OSError) as os_ex:
                LOG.error("Exception in step #%d: %s", i, str(action),
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
        sub_actns = [a.__str__(indent + 1) for a in self._actions]
        sub_actns = "\n".join(sub_actns)
        return textwrap.indent("* All required:\n" + sub_actns, indent * " ")


class CleanExtra(Step):
    NAME = "CLEAN EXTRA"
    DESCRIPTION = "Cleans the extra directories."

    @notify_step_begin_end
    def __call__(self):
        if not CFG['clean'].value():
            return StepResult.OK

        paths = CFG["cleanup_paths"].value()
        for p in paths:
            if os.path.exists(p):
                rm("-r", p)
        self.status = StepResult.OK

    def __str__(self, indent=0):
        paths = CFG["cleanup_paths"].value()
        lines = []
        for p in paths:
            lines.append(textwrap.indent("* Clean the directory: {0}".format(
                p), indent * " "))
        return "\n".join(lines)
