"""
BenchBuild's skeleton for experiments.

An benchbuild.experiment defines a series of phases that constitute a
benchbuild compatible experiment. This is the default implementation of an
experiment.

Clients can derive from class class::benchbuild.experiment.Experiment and
override the methods relvant to their experiment.

An experiment can have a variable number of phases / steps / substeps.

Phases / Steps / Substeps
-------------------------

All phases/steps/substeps support being used as a context manager. All 3 of
them catch ProcessExecutionErrors that may be thrown from plumbum, without
aborting the whole experiment. However, an error is tracked.

Actions
-------

An experiment performs the following actions in order:
    1. clean - Clean any previous runs that collide with our directory
    2. prepare - Prepare the experiment, this is a good place to copy relevant
                 files over for testing.
    3. run (run_tests) - Run the experiment. The 'meat' lies here. Override
        This to perform all your experiment needs.

"""
import copy
import typing as t
import uuid
from abc import abstractmethod

import attr

from benchbuild.settings import CFG
from benchbuild.utils.actions import (Build, Clean, CleanExtra, Configure,
                                      Download, MakeBuildDir, Prepare,
                                      RequireAll, Run)


class ExperimentRegistry(type):
    """Registry for benchbuild experiments."""

    experiments = {}

    def __init__(cls, name, bases, dict):
        """Register a project in the registry."""
        super(ExperimentRegistry, cls).__init__(name, bases, dict)

        if cls.NAME is not None:
            ExperimentRegistry.experiments[cls.NAME] = cls


@attr.s(cmp=False)
class Experiment(object, metaclass=ExperimentRegistry):
    """
    A series of commands executed on a project that form an experiment.

    The default implementation should provide a sane environment for all
    derivates.

    One important task executed by the basic implementation is setting up
    the default set of projects that belong to this project.
    As every project gets registered in the ProjectFactory, the experiment
    gets a list of experiment names that work as a filter.

    """

    NAME: t.ClassVar[str] = None

    def __new__(cls, *args, **kwargs):
        """Create a new experiment instance and set some defaults."""
        new_self = super(Experiment, cls).__new__(cls)
        if cls.NAME is None:
            raise AttributeError(
                "{0} @ {1} does not define a NAME class attribute.".format(
                    cls.__name__, cls.__module__))
        return new_self

    name: str = attr.ib(default=attr.Factory(
        lambda self: type(self).NAME, takes_self=True))

    projects: t.List['benchbuild.project.Project'] = \
        attr.ib(default=attr.Factory(list))

    id: str = attr.ib()
    @id.default
    def default_id(self):
        cfg_exps = CFG["experiments"].value()
        if self.name in cfg_exps:
            _id = cfg_exps[self.name]
        else:
            _id = uuid.uuid4()
            cfg_exps[self.name] = _id
            CFG["experiments"] = cfg_exps
        return _id

    @abstractmethod
    def actions_for_project(self, project):
        """
        Get the actions a project wants to run.

        Args:
            project (benchbuild.Project): the project we want to run.
        """

    def actions(self):
        actions = []

        for project in self.projects:
            p = self.projects[project](self)
            actions.append(Clean(p))
            actions.append(
                RequireAll(obj=p,
                           actions=self.actions_for_project(p)))

        actions.append(CleanExtra(self))
        return actions

    @staticmethod
    def default_runtime_actions(project):
        """Return a series of actions for a run time experiment."""
        return [
            MakeBuildDir(project),
            Prepare(project),
            Download(project),
            Configure(project),
            Build(project),
            Run(project),
            Clean(project)
        ]

    @staticmethod
    def default_compiletime_actions(project):
        """Return a series of actions for a compile time experiment."""
        return [
            MakeBuildDir(project),
            Prepare(project),
            Download(project),
            Configure(project),
            Build(project),
            Clean(project)
        ]


class Configuration(object):
    """Build a set of experiment actions out of a list of configurations."""

    def __init__(self, project=None, config=None):
        _project = copy.deepcopy(project)
        self.config = {}
        if project is not None and config is not None:
            self.config[_project] = config

    def __add__(self, rhs):
        self.config.update(rhs.config)
