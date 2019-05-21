"""Experiments

An experiment in benchbuild is a simple list of actions that need to be
executed on every project that is part of the experiment.
Every `callable` can serve as an action.

However, benchbuild provides many predefined actions that can
be reused by implementations in the `benchbuild.utils.actions` module.
Furthermore, if you do not need to control the default order of
actions for a run-time or a compile-time experiment you can reuse the
`Experiment.default_runtime_actions` or
`Experiment.default_compiletime_actions`.

Besides the list of actions, it is also the responsibility of an experiment
to configure each single project that should take part in an experiment.
This includes setting appropriate `CFLAGS`, `LDFLAGS` and any additional
metadata that has to be added to binary runs for later evaluation.

Example
-------
```python
class HelloExperiment(Experiment):
    pass
```

"""
import collections
import copy
import uuid
from abc import abstractmethod

import attr

from benchbuild.settings import CFG
from benchbuild.utils.actions import (Any, Clean, CleanExtra, Compile,
                                      Containerize, Echo, MakeBuildDir,
                                      RequireAll, Run)


class ExperimentRegistry(type):
    """Registry for benchbuild experiments."""

    experiments = {}

    def __init__(cls, name, bases, _dict):
        """Register a project in the registry."""
        super(ExperimentRegistry, cls).__init__(name, bases, _dict)

        if cls.NAME is not None:
            ExperimentRegistry.experiments[cls.NAME] = cls


@attr.s(cmp=False)
class Experiment(metaclass=ExperimentRegistry):
    """
    A series of commands executed on a project that form an experiment.

    The default implementation should provide a sane environment for all
    derivates.

    One important task executed by the basic implementation is setting up
    the default set of projects that belong to this project.
    As every project gets registered in the ProjectFactory, the experiment
    gets a list of experiment names that work as a filter.

    Attributes:
        name (str): The name of the experiment, defaults to NAME
        projects (:obj:`list` of `benchbuild.project.Project`):
            A list of projects that is assigned to this experiment.
        id (str):
            A uuid encoded as :obj:`str` used to identify this
            instance of experiment. Equivalent to the `experiment_group`
            in the database scheme.
    """

    NAME = None
    SCHEMA = None

    def __new__(cls, *args, **kwargs):
        """Create a new experiment instance and set some defaults."""
        del args, kwargs  # Temporarily unused
        new_self = super(Experiment, cls).__new__(cls)
        if cls.NAME is None:
            raise AttributeError(
                "{0} @ {1} does not define a NAME class attribute.".format(
                    cls.__name__, cls.__module__))
        return new_self

    name = attr.ib(
        default=attr.Factory(lambda self: type(self).NAME, takes_self=True))

    projects = \
        attr.ib(default=attr.Factory(list))

    id = attr.ib()

    @id.default
    def default_id(self):
        cfg_exps = CFG["experiments"].value
        if self.name in cfg_exps:
            _id = cfg_exps[self.name]
        else:
            _id = uuid.uuid4()
            cfg_exps[self.name] = _id
            CFG["experiments"] = cfg_exps
        return _id

    @id.validator
    def validate_id(self, _, new_id):
        if not isinstance(new_id, uuid.UUID):
            raise TypeError("%s expected to be '%s' but got '%s'" %
                            (str(new_id), str(uuid.UUID), str(type(new_id))))

    schema = attr.ib()

    @schema.default
    def default_schema(self):
        return type(self).SCHEMA

    @schema.validator
    def validate_schema(self, _, new_schema):
        if new_schema is None:
            return True
        if isinstance(new_schema, collections.abc.Iterable):
            return True
        return False

    @abstractmethod
    def actions_for_project(self, project):
        """
        Get the actions a project wants to run.

        Args:
            project (benchbuild.Project): the project we want to run.
        """

    def actions(self):
        """
        Common setup required to run this experiment on all projects.
        """
        actions = []

        for project in self.projects:
            prj_cls = self.projects[project]

            prj_actions = []
            for version in self.sample(prj_cls, prj_cls.versions()):
                p = prj_cls(self, version=version)

                atomic_actions = [
                    Clean(p),
                    MakeBuildDir(p),
                    Echo(message="Selected {0} with version {1}".format(
                        p.name, p.version)),
                    Containerize(obj=p, actions=self.actions_for_project(p))
                ]
                prj_actions.append(RequireAll(actions=atomic_actions))
            actions.extend(prj_actions)

        actions.append(CleanExtra(self))
        return actions

    def sample(self, prj_cls, versions=None):
        """
        Sample all avilable versions.

        The default sampling returns the latest version only.
        You can override this behavior in custom experiments.

        Args:
            prj_cls (class of benchbuild.project.Project):
                The project class we sample versions for.
            versions (list of str):
                An ordered list of versions for the given prj_cls.
                You can assume that the versions in this list are
                valid version numbers for prj_cls.

        Returns:
            A list of version strings.

        Assumptions:
            versions:
                * semantically ordered, descending.
                * for version in versions:
                    version in prj_cls.versions()
        """
        if versions is None:
            versions = prj_cls.versions()

        if not versions:
            # early return if version list is empty
            return

        head, *tail = versions

        yield head
        if bool(CFG["versions"]["full"]):
            for v in tail:
                yield v

    @staticmethod
    def default_runtime_actions(project):
        """Return a series of actions for a run time experiment."""
        return [Compile(project), Run(project), Clean(project)]

    @staticmethod
    def default_compiletime_actions(project):
        """Return a series of actions for a compile time experiment."""
        return [Compile(project), Clean(project)]


class Configuration:
    """Build a set of experiment actions out of a list of configurations."""

    def __init__(self, project=None, config=None):
        _project = copy.deepcopy(project)
        self.config = {}
        if project is not None and config is not None:
            self.config[_project] = config

    def __add__(self, rhs):
        self.config.update(rhs.config)
