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
import typing as tp
import uuid
from abc import abstractmethod

import attr

import benchbuild.utils.actions as actns
from benchbuild.settings import CFG
from benchbuild.utils.requirements import Requirement

from . import source
from .project import Project

Actions = tp.MutableSequence[actns.Step]
ProjectT = tp.Type[Project]
Projects = tp.List[ProjectT]


class ExperimentRegistry(type):
    """Registry for benchbuild experiments."""

    experiments = {}

    def __new__(mcs: tp.Type[tp.Any], name: str, bases: tp.Tuple[type, ...],
                attrs: tp.Dict[str, tp.Any]) -> tp.Any:
        """Register a project in the registry."""
        cls = super(ExperimentRegistry, mcs).__new__(mcs, name, bases, attrs)
        if bases and 'NAME' in attrs:
            ExperimentRegistry.experiments[cls.NAME] = cls
        return cls


@attr.s(eq=False)
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
        requirements (:obj:`list` of :obj:`Requirement`)
            A list of specific requirements that are used to configure the
            execution environment.
        projects (:obj:`list` of `benchbuild.project.Project`):
            A list of projects that is assigned to this experiment.
        id (str):
            A uuid encoded as :obj:`str` used to identify this
            instance of experiment. Equivalent to the `experiment_group`
            in the database scheme.
    """

    NAME: tp.ClassVar[str] = ''
    SCHEMA = None
    REQUIREMENTS: tp.List[Requirement] = []

    def __new__(cls, *args, **kwargs):
        """Create a new experiment instance and set some defaults."""
        del args, kwargs  # Temporarily unused
        new_self = super(Experiment, cls).__new__(cls)
        if not cls.NAME:
            raise AttributeError(
                "{0} @ {1} does not define a NAME class attribute.".format(
                    cls.__name__, cls.__module__))
        return new_self

    name: str = attr.ib(
        default=attr.Factory(lambda self: type(self).NAME, takes_self=True))

    projects: Projects = \
        attr.ib(default=attr.Factory(dict))

    id = attr.ib()

    @id.default
    def default_id(self) -> uuid.UUID:
        cfg_exps = CFG["experiments"].value
        if self.name in cfg_exps:
            _id = cfg_exps[self.name]
        else:
            _id = uuid.uuid4()
            cfg_exps[self.name] = _id
            CFG["experiments"] = cfg_exps
        return _id

    @id.validator
    def validate_id(self, _: tp.Any, new_id: uuid.UUID) -> None:
        if not isinstance(new_id, uuid.UUID):
            raise TypeError("%s expected to be '%s' but got '%s'" %
                            (str(new_id), str(uuid.UUID), str(type(new_id))))

    schema = attr.ib()

    @schema.default
    def default_schema(self):
        return type(self).SCHEMA

    @schema.validator
    def validate_schema(self, _: tp.Any, new_schema) -> bool:
        if new_schema is None:
            return True
        if isinstance(new_schema, collections.abc.Iterable):
            return True
        return False

    @abstractmethod
    def actions_for_project(self, project: Project) -> Actions:
        """
        Get the actions a project wants to run.

        Args:
            project (benchbuild.Project): the project we want to run.
        """

    def actions(self) -> Actions:
        """
        Common setup required to run this experiment on all projects.
        """
        actions = []

        for prj_cls in self.projects:
            prj_actions: Actions = []

            project_variants = source.product(*prj_cls.SOURCE)
            for variant in project_variants:
                var_context = source.context(*variant)
                version_str = source.to_str(*variant)

                p = prj_cls(self, variant=var_context)
                atomic_actions: Actions = [
                    actns.Clean(p),
                    actns.MakeBuildDir(p),
                    actns.Echo(message="Selected {0} with version {1}".format(
                        p.name, version_str)),
                    actns.ProjectEnvironment(p),
                    actns.Containerize(obj=p,
                                       actions=self.actions_for_project(p))
                ]

                prj_actions.append(actns.RequireAll(actions=atomic_actions))
            actions.extend(prj_actions)

        if actions:
            actions.append(actns.CleanExtra(self))
        return actions

    def sample(self,
               prj_cls: ProjectT,
               versions: tp.Optional[tp.List[str]] = None) -> tp.List[str]:
        """
        Sample all available versions.

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
    def default_runtime_actions(project: Project) -> Actions:
        """Return a series of actions for a run time experiment."""
        return [
            actns.Compile(project),
            actns.Run(project),
            actns.Clean(project)
        ]

    @staticmethod
    def default_compiletime_actions(project: Project) -> Actions:
        """Return a series of actions for a compile time experiment."""
        return [actns.Compile(project), actns.Clean(project)]


class Configuration:
    """Build a set of experiment actions out of a list of configurations."""

    def __init__(self, project=None, config=None):
        _project = copy.deepcopy(project)
        self.config = {}
        if project is not None and config is not None:
            self.config[_project] = config

    def __add__(self, rhs):
        self.config.update(rhs.config)
