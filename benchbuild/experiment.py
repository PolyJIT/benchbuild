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
import copy
import typing as tp
import uuid
from abc import abstractmethod

import attr

import benchbuild.utils.actions as actns
from benchbuild.environments.domain import declarative
from benchbuild.project import build_dir
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

    def __new__(
        mcs: tp.Type[tp.Any], name: str, bases: tp.Tuple[type, ...],
        attrs: tp.Dict[str, tp.Any], *args: tp.Any, **kwargs: tp.Any
    ) -> tp.Any:
        """Register a project in the registry."""
        cls = super(ExperimentRegistry,
                    mcs).__new__(mcs, name, bases, attrs, *args, **kwargs)
        if bases and "NAME" in attrs:
            ExperimentRegistry.experiments[attrs["NAME"]] = cls
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

    NAME: tp.ClassVar[str] = ""
    SCHEMA = None
    REQUIREMENTS: tp.List[Requirement] = []
    CONTAINER: tp.ClassVar[declarative.ContainerImage
                          ] = declarative.ContainerImage()

    def __new__(cls, *args, **kwargs):
        """Create a new experiment instance and set some defaults."""
        del args, kwargs  # Temporarily unused
        new_self = super(Experiment, cls).__new__(cls)
        if not cls.NAME:
            raise AttributeError(
                "{0} @ {1} does not define a NAME class attribute.".format(
                    cls.__name__, cls.__module__
                )
            )
        return new_self

    name: str = attr.ib(
        default=attr.Factory(lambda self: type(self).NAME, takes_self=True)
    )

    projects: Projects = attr.ib(default=attr.Factory(list))

    id = attr.ib()

    @id.default
    def default_id(self) -> uuid.UUID:
        cfg_exps = CFG["experiments"].value
        if self.name in cfg_exps:
            _id: uuid.UUID = cfg_exps[self.name]
        else:
            _id = uuid.uuid4()
            cfg_exps[self.name] = _id
            CFG["experiments"] = cfg_exps
        return _id

    @id.validator
    def validate_id(self, _: tp.Any, new_id: uuid.UUID) -> None:
        if not isinstance(new_id, uuid.UUID):
            raise TypeError(
                "%s expected to be '%s' but got '%s'" %
                (str(new_id), str(uuid.UUID), str(type(new_id)))
            )

    schema = attr.ib()

    @schema.default
    def default_schema(self):
        return type(self).SCHEMA

    container: declarative.ContainerImage = attr.ib()

    @container.default
    def default_container(self) -> declarative.ContainerImage:
        return type(self).CONTAINER

    @schema.validator
    def validate_schema(self, _: tp.Any, new_schema) -> bool:
        if new_schema is None:
            return True
        if isinstance(new_schema, tp.Iterable):
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
        actions: Actions = []

        for prj_cls in self.projects:
            prj_actions: Actions = []

            for revision in self.sample(prj_cls):
                version_str = str(revision)

                p = prj_cls(revision)
                p.builddir = build_dir(self, p)
                atomic_actions: Actions = [
                    actns.Clean(p),
                    actns.MakeBuildDir(p),
                    actns.Echo(
                        message="Selected {0} with version {1}".
                        format(p.name, version_str)
                    ),
                    actns.ProjectEnvironment(p),
                ]
                atomic_actions.extend(self.actions_for_project(p))

                prj_actions.append(actns.RequireAll(actions=atomic_actions))
            actions.extend(prj_actions)

        if actions:
            actions.append(actns.CleanExtra())
        return actions

    @classmethod
    def sample(cls, prj_cls: ProjectT) -> tp.Sequence[source.Revision]:
        """
        Sample all versions provided by the project.

        This will enumerate all version combinations of this project.

        Args:
            prj_cls: The project type to enumerate all versions from.

        Returns:
            A list of all sampled project revisions.
        """
        revisions = source.enumerate_revisions(prj_cls)

        if bool(CFG["versions"]["full"]):
            return revisions

        if len(revisions) > 0:
            return [revisions[0]]
        raise ValueError("At least one variant is required!")

    def default_runtime_actions(self, project: Project) -> Actions:
        """Return a series of actions for a run time experiment."""
        return [
            actns.Compile(project),
            actns.RunWorkloads(project, experiment=self),
            # actns.Run(project, experiment=self),
            actns.Clean(project),
        ]

    def default_compiletime_actions(self, project: Project) -> Actions:
        """Return a series of actions for a compile time experiment."""
        return [actns.Compile(project), actns.Clean(project)]


ExperimentIndex = tp.Dict[str, tp.Type[Experiment]]


class Configuration:
    """Build a set of experiment actions out of a list of configurations."""

    def __init__(self, project=None, config=None):
        _project = copy.deepcopy(project)
        self.config = {}
        if project is not None and config is not None:
            self.config[_project] = config

    def __add__(self, rhs):
        self.config.update(rhs.config)


def discovered() -> tp.Dict[str, tp.Type[Experiment]]:
    """Return all discovered experiments."""
    return ExperimentRegistry.experiments
