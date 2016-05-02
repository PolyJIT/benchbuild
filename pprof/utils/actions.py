"""
This defines classes that can be used to implement a series of Actions.
"""
from pprof.settings import CFG
from pprof.utils.db import persist_experiment
from pprof.utils.run import GuardedRunException

from plumbum import local
from plumbum.cmd import mkdir, rm
from plumbum import ProcessExecutionError
from functools import partial, wraps
from datetime import datetime
from logging import error
import os
import logging
import sys
import traceback
import warnings
from abc import abstractmethod, abstractproperty, ABCMeta
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
    _log = logging.getLogger(name='pprof.steps')

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
            result.__call__ = log_before_after(NAME, DESCRIPTION)(
                    to_step_result(result.__call__)
                )
        else:
            result.__call__ = to_step_result(result.__call__)

        return result


class Clean:
    pass

class Step(metaclass=StepClass):
    NAME = None
    DESCRIPTION = None

    def __init__(self, project_or_experiment, action_fn=None):
        self._obj = project_or_experiment
        self._action_fn = action_fn

    def __call__(self):
        if not self._action_fn:
            return
        self._action_fn()

    def onerror(self):
        Clean(self._obj)()

class Clean(Step):
    NAME = "CLEAN"
    DESCRIPTION = "Cleans the build directory"

    def __call__(self):
        if not CFG['clean'].value():
            return
        if not self._obj:
            return
        obj_builddir = os.path.abspath(self._obj.builddir)
        if os.path.exists(obj_builddir):
            rm("-rf", obj_builddir)


class MakeBuildDir(Step):
    NAME = "MKDIR"
    DESCRIPTION = "Create the build directory"

    def __call__(self):
        if not self._obj:
            return
        if not os.path.exists(self._obj.builddir):
            mkdir(self._obj.builddir)

class Prepare(Step):
    NAME = "PREPARE"
    DESCRIPTION = "Prepare project build folder"

    def __init__(self, project):
        super(Prepare, self).__init__(project, project.prepare)

class Download(Step):
    NAME = "DOWNLOAD"
    DESCRIPTION = "Download project source files"

    def __init__(self, project):
        super(Download, self).__init__(project, project.download)

class Configure(Step):
    NAME = "CONFIGURE"
    DESCRIPTION = "Configure project source files"

    def __init__(self, project):
        super(Configure, self).__init__(project, project.configure)

class Build(Step):
    NAME = "BUILD"
    DESCRIPTION = "Build the project"

    def __init__(self, project):
        super(Build, self).__init__(project, project.build)

class Run(Step):
    NAME = "RUN"
    DESCRIPTION = "Execute the run action"

    def __init__(self, project):
        action_fn = partial(project.run, project.runtime_extension)
        super(Run, self).__init__(project, action_fn)

    def begin_transaction(self):
        experiment, session = persist_experiment(self._obj.experiment)
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
        if not self._obj:
            return
        if not self._action_fn:
            return

        experiment, session = self.begin_transaction()
        try:
            with local.env(PPROF_EXPERIMENT_ID=str(CFG["experiment_id"])):
                self._action_fn()
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


class Echo(Step):
    NAME = 'ECHO'
    DESCRIPTION = 'Print a message.'

    def __init__(self, message):
        self._message = message

    def __call__(self):
        print(self._message)

class ForAll(Step):
    def __init__(self, actions):
        self._actions = actions
        self._log = logging.getLogger('pprof.steps')
        self._exlog = logging.getLogger('pprof')

    def __call__(self):
        for action in self._actions:
            try:
                result = action()
            except ProcessExecutionError as proc_ex:
                self._exlog.error(u'\n' + proc_ex.stderr)
                result = StepResult.ERROR
            except (OSError, GuardedRunException) as os_ex:
                self._exlog.error(os_ex)
                result = StepResult.ERROR
            if not (result == StepResult.OK):
                action.onerror()
                return result
