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

from plumbum import local

import benchbuild.project as p
from benchbuild.settings import CFG
from benchbuild.utils.actions import (Build, Clean, CleanExtra, Configure,
                                      Download, MakeBuildDir, Prepare,
                                      RequireAll, Run)


def get_group_projects(group: str, experiment) -> t.List[p.Project]:
    """
    Get a list of project names for the given group.

    Filter the projects assigned to this experiment by group.

    Args:
        group (str): The group.
        experiment (benchbuild.Experiment): The experiment we draw our projects
            to filter from.

    Returns (list):
        A list of project names for the group that are supported by this
        experiment.
    """
    group = []
    projects = experiment.projects
    for name in projects:
        project = projects[name]

        if project.group == group:
            group.append(name)
    return group


class ExperimentRegistry(type):
    """Registry for benchbuild experiments."""

    experiments = {}

    def __init__(cls, name, bases, dict):
        """Register a project in the registry."""
        super(ExperimentRegistry, cls).__init__(name, bases, dict)

        if cls.NAME is not None:
            ExperimentRegistry.experiments[cls.NAME] = cls


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

    NAME = None

    def __new__(cls, *args, **kwargs):
        """Create a new experiment instance and set some defaults."""
        new_self = super(Experiment, cls).__new__(cls)
        if cls.NAME is None:
            raise AttributeError(
                "{0} @ {1} does not define a NAME class attribute.".format(
                    cls.__name__, cls.__module__))
        new_self.name = cls.NAME
        return new_self

    def __init__(self, projects=None, group=None):
        self.sourcedir = CFG["src_dir"].value()
        self.builddir = str(CFG["build_dir"].value())
        self.testdir = CFG["test_dir"].value()
        self._actions = []

        cfg_exps = CFG["experiments"].value()
        if self.name in cfg_exps:
            self.id = cfg_exps[self.name]
        else:
            self.id = str(uuid.uuid4())
            cfg_exps[self.name] = self.id
            CFG["experiments"] = cfg_exps

        self.projects = p.populate(projects, group)

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
            actions.append(RequireAll(self.actions_for_project(p)))

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
