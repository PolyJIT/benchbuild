"""
This defines classes that can be used to implement a series of Actions.
"""
from benchbuild.settings import CFG
from benchbuild.utils.db import persist_experiment
from benchbuild.utils.run import GuardedRunException

from plumbum import local
from benchbuild.utils.cmd import mkdir, rm, rmdir
from plumbum import ProcessExecutionError
from functools import partial, wraps
from datetime import datetime
from logging import error
import os
import logging
import sys
import traceback
import warnings
import textwrap
from abc import ABCMeta
from enum import Enum, unique


@unique
class StepResult(Enum):
    OK = 1,
    ERROR = 2


def to_step_result(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        res = f(*args, **kwargs)
        if not res:
            res = StepResult.OK
        return res

    return wrapper


def log_before_after(name, desc):
    _log = logging.getLogger(name='benchbuild.steps')

    def func_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            _log.info("\n{} - {}".format(name, desc))
            res = f(*args, **kwargs)
            if res == StepResult.OK:
                _log.info("{} - OK\n".format(name))
            else:
                _log.error("{} - ERROR\n".format(name))
            return res

        return wrapper

    return func_decorator


class StepClass(ABCMeta):
    def __new__(metacls, name, bases, namespace, **kwds):
        result = ABCMeta.__new__(metacls, name, bases, dict(namespace))

        NAME = result.NAME
        DESCRIPTION = result.DESCRIPTION
        if NAME and DESCRIPTION:
            result.__call__ = log_before_after(
                NAME, DESCRIPTION)(to_step_result(result.__call__))
        else:
            result.__call__ = to_step_result(result.__call__)

        return result


class Step(metaclass=StepClass):
    NAME = None
    DESCRIPTION = None

    def __init__(self, project_or_experiment, action_fn=None):
        self._obj = project_or_experiment
        self._action_fn = action_fn

    def __len__(self):
        return 1

    def __call__(self):
        if not self._action_fn:
            return
        self._action_fn()

    def __str__(self, indent=0):
        return textwrap.indent(
            "* {0}: Execute configured action.".format(self._obj.name),
            indent * " ")

    def onerror(self):
        Clean(self._obj)()


class Clean(Step):
    NAME = "CLEAN"
    DESCRIPTION = "Cleans the build directory"

    def __init__(self, project_or_experiment, action_fn=None, check_empty=False):
        super(Clean, self).__init__(project_or_experiment, action_fn)
        self.check_empty = check_empty

    def __clean_mountpoints__(self, root):
        """
        Unmount any remaining mountpoints under :root.

        Args:
            root: All UnionFS-mountpoints under this directory will be unmounted.
        """
        import psutil
        umount_paths = []
        for part in psutil.disk_partitions(all=True):
            if os.path.commonpath([part.mountpoint, root]) == root:
                if not part.fstype == "fuse.unionfs":
                    logging.error(
                        "NON-UnionFS mountpoint found under {0}".format(root))
                else:
                    umount_paths.append(part.mountpoint)


    def __call__(self):
        if not CFG['clean'].value():
            return
        if not self._obj:
            return
        obj_builddir = os.path.abspath(self._obj.builddir)
        if os.path.exists(obj_builddir):
            self.__clean_mountpoints__(obj_builddir)
            if self.check_empty:
                rmdir(obj_builddir, retcode=None)
            else:
                rm("-rf", obj_builddir)

    def __str__(self, indent=0):
        return textwrap.indent("* {0}: Clean the directory: {1}".format(
            self._obj.name, self._obj.builddir), indent * " ")


class MakeBuildDir(Step):
    NAME = "MKDIR"
    DESCRIPTION = "Create the build directory"

    def __call__(self):
        if not self._obj:
            return
        if not os.path.exists(self._obj.builddir):
            mkdir(self._obj.builddir)

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
        action_fn = partial(project.run, project.runtime_extension)
        super(Run, self).__init__(project, action_fn)

    def __call__(self):
        if not self._obj:
            return
        if not self._action_fn:
            return

        with local.env(BB_EXPERIMENT_ID=str(CFG["experiment_id"]),
                       BB_USE_DATABSE=1):
            self._action_fn()

    def __str__(self, indent=0):
        return textwrap.indent(
            "* {0}: Execute run-time tests.".format(self._obj.name),
            indent * " ")


class Echo(Step):
    NAME = 'ECHO'
    DESCRIPTION = 'Print a message.'

    def __init__(self, message):
        self._message = message

    def __str__(self, indent=0):
        return textwrap.indent("* echo: {0}".format(self._message),
                               indent * " ")

    def __call__(self):
        print()
        print(self._message)
        print()


class Any(Step):
    NAME = "ANY"
    DESCRIPTION = "Just run all actions, no questions asked."

    def __init__(self, actions):
        self._actions = actions
        self._exlog = logging.getLogger('benchbuild')
        super(Any, self).__init__(None, None)

    def __len__(self):
        return sum([len(x) for x in self._actions])

    def __call__(self):
        length = len(self._actions)
        cnt = 0
        for a in self._actions:
            result = a()
            cnt = cnt + 1
            if result == StepResult.ERROR:
                self._exlog.warn("{0} actions left in queue".format(
                    length - cnt))
        return StepResult.OK

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
            [Echo("Start experiment: {0}".format(experiment.name))] + actions
        super(Experiment, self).__init__(actions)

    def begin_transaction(self):
        experiment, session = persist_experiment(self._experiment)
        if experiment.begin is None:
            experiment.begin = datetime.now()
        else:
            experiment.begin = min(experiment.begin, datetime.now())
        session.add(experiment)
        session.commit()
        return experiment, session

    def end_transaction(self, experiment, session):
        if experiment.end is None:
            experiment.end = datetime.now()
        else:
            experiment.end = max(experiment.end, datetime.now())
        session.add(experiment)
        session.commit()

    def __call__(self):
        result = StepResult.OK

        experiment, session = self.begin_transaction()
        try:
            for a in self._actions:
                with local.env(BB_EXPERIMENT_ID=str(CFG["experiment_id"])):
                    result = a()
        except KeyboardInterrupt:
            error("User requested termination.")
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            formatted = "".join(traceback.format_exception(exc_type, exc_value,
                                                           exc_traceback))
            warnings.warn(formatted, category=RuntimeWarning)
            print("Shutting down...")
        finally:
            self.end_transaction(experiment, session)

        return result

    def __str__(self, indent=0):
        sub_actns = [a.__str__(indent + 1) for a in self._actions]
        sub_actns = "\n".join(sub_actns)
        return textwrap.indent(
            "\nExperiment: {0}\n".format(self._experiment.name) + sub_actns,
            indent * " ")


class RequireAll(Step):
    def __init__(self, actions):
        self._actions = actions
        self._exlog = logging.getLogger('benchbuild')
        super(RequireAll, self).__init__(None, None)

    def __len__(self):
        return sum([len(x) for x in self._actions])

    def __call__(self):
        for i, action in enumerate(self._actions):
            try:
                result = action()
            except ProcessExecutionError as proc_ex:
                self._exlog.exception("Plumbum exception caught.")
                result = StepResult.ERROR
            except (OSError, GuardedRunException) as os_ex:
                self._exlog.exception("Exception in step #{0}: {1}".format(
                    i, action))
                result = StepResult.ERROR

            if result != StepResult.OK:
                self._exlog.error("Execution of #{0}: '{1}' failed.".format(
                    i, str(action)))
                action.onerror()
                return result

    def __str__(self, indent=0):
        sub_actns = [a.__str__(indent + 1) for a in self._actions]
        sub_actns = "\n".join(sub_actns)
        return textwrap.indent("* All required:\n" + sub_actns, indent * " ")


class CleanExtra(Step):
    NAME = "CLEAN EXTRA"
    DESCRIPTION = "Cleans the extra directories."

    def __call__(self):
        if not CFG['clean'].value():
            return

        paths = CFG["cleanup_paths"].value()
        for p in paths:
            if os.path.exists(p):
                rm("-r", p)

    def __str__(self, indent=0):
        paths = CFG["cleanup_paths"].value()
        lines = []
        for p in paths:
            lines.append(textwrap.indent("* Clean the directory: {0}".format(
                p), indent * " "))
        return "\n".join(lines)
