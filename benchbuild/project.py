"""Project

A project in benchbuild is an abstract representation of a software
system that can live in various stages throughout an experiment.
It defines two extension points for an experiment to attach on, the
compile-time phase and the (optional) run-time phase.

An experiment can intercept the compilation phase of a project and perform
any experiment that requires the source artifacts as input.

Furthermore, it is possible to intercept a project's run-time pahse with
a measurement.

The project definition ensures that all experiments run through the same
series of commands in both phases and that all experiments run inside
a separate build directory in isolation of one another.
"""
import copy
import logging
from typing import List, Tuple, Optional, Mapping, Type
import uuid
from abc import abstractmethod
from functools import partial
from os import getenv

import attr
from plumbum import ProcessExecutionError, local
from pygtrie import StringTrie

import benchbuild as bb

from benchbuild import signals
from benchbuild.extensions import compiler
from benchbuild.extensions import run as ext_run
from benchbuild.settings import CFG
from benchbuild.utils import db, run, unionfs

LOG = logging.getLogger(__name__)


class ProjectRegistry(type):
    """Registry for benchbuild projects."""

    projects = StringTrie()

    def __init__(cls, name, bases, attrs):
        """Register a project in the registry."""
        super(ProjectRegistry, cls).__init__(name, bases, attrs)

        if None not in {cls.NAME, cls.DOMAIN, cls.GROUP}:
            key = "{name}/{group}".format(name=cls.NAME, group=cls.GROUP)
            ProjectRegistry.projects[key] = cls


class ProjectDecorator(ProjectRegistry):
    """
    Decorate the interface of a project with the in_builddir decorator.

    This is just a small safety net for benchbuild users, because we make
    sure to run every project method in the project's build directory.
    """

    decorated_methods = ["redirect", "compile", "run_tests"]

    def __init__(cls, name, bases, attrs):
        unionfs_deco = None
        if CFG["unionfs"]["enable"]:
            rw_dir = str(CFG["unionfs"]["rw"])
            unionfs_deco = partial(unionfs.unionfs, rw=rw_dir)
        config_deco = run.store_config

        methods = ProjectDecorator.decorated_methods
        for key, value in attrs.items():
            if (key in methods) and hasattr(cls, key):
                wrapped_fun = value
                wrapped_fun = config_deco(wrapped_fun)

                if unionfs_deco is not None:
                    wrapped_fun = unionfs_deco()(wrapped_fun)

                wrapped_fun = run.in_builddir('.')(wrapped_fun)
                setattr(cls, key, wrapped_fun)

        super(ProjectDecorator, cls).__init__(name, bases, attrs)


@attr.s
class Project(metaclass=ProjectDecorator):
    """Abstract class for benchbuild projects.

    A project is an arbitrary software system usable by benchbuild in
    experiments.
    Subclasses of Project are registered automatically by benchbuild, if
    imported in the same interpreter session. For this to happen, you must list
    the in the settings under plugins -> projects.

    A project implementation *must* provide the following method:
        compile: Downloads & Compiles the source.

    A project implementation *may* provide the following functions:
        run_tests: Wrap any binary that has to be run under the
            runtime_extension wrapper and execute an implementation defined
            set of run-time tests.
        clean: Clean the project's build directory. Defaults to
            recursive 'rm' on the build directory and can be disabled
            by setting the environment variable ``BB_CLEAN=false``.

    Raises:
        AttributeError: Class definition raises an attribute error, if
            the implementation does not provide a value for the attributes
            `NAME`, `DOMAIN`, and `GROUP`
        TypeError: Validation of properties may throw a TypeError.

    Attributes:
        experiment (benchbuild.experiment.Experiment):
            The experiment this project is assigned to.
        name (str, optional):
            The name of this project. Defaults to `NAME`.
        domain (str, optional):
            The application domain of this project. Defaults to `DOMAIN`.
        group (str, optional):
            The group this project belongs to. Defaults to `GROUP`.
        container (benchbuild.utils.container.Container, optional):
            A uchroot compatible container that we can use for this project.
            Defaults to `benchbuild.utils.container.Gentoo`.
        builddir (str, optional):
            The build directory for this project. Auto generated, if not set.
        cflags (:obj:`list` of :obj:`str`, optional)
            A list of cflags used, for compilation of this project.
        ldflags (:obj:`list` of :obj:`str`, optional)
            A list of ldflags used, for compilation of this project.
        run_uuid (uuid.UUID, optional):
            An UUID that identifies all binaries executed by a single run of
            this project. In the database schema this is named the 'run_group'.
        compiler_extension (Callable[str, iterable[str], RunInfo], optional):
            A composable extension that will be used in place of the real
            compiler. Defaults to running the compiler with a timeout command
            wrapped around it.
        runtime_extension (Callable[str, iterable[str], RunInfo], optional):
            A composable extension that will be used in place of any binary
            this project
            wants to execute. Which binaries to replace is defined by the
            implementation using `benchbuild.utils.wrapping.wrap`.
            Defaults to None.
    """
    CONTAINER = None
    DOMAIN: str = ""
    GROUP: str = ""
    NAME: str = ""
    SOURCE: List[bb.downloads.BaseSource] = []

    def __new__(cls, *args, **kwargs):
        """Create a new project instance and set some defaults."""
        new_self = super(Project, cls).__new__(cls)
        mod_ident = f'{cls.__name__} @ {cls.__module__}'
        if not cls.NAME:
            raise AttributeError(
                f'{mod_ident} does not define a NAME class attribute.')
        if not cls.DOMAIN:
            raise AttributeError(
                f'{mod_ident} does not define a DOMAIN class attribute.')
        if not cls.GROUP:
            raise AttributeError(
                f'{mod_ident} does not define a GROUP class attribute.')
        return new_self

    experiment = attr.ib()

    variant: bb.variants.VariantContext = attr.ib()

    @variant.default
    def __default_variant(self) -> bb.variants.VariantContext:
        return bb.downloads.default(type(self).SOURCE)

    name: str = attr.ib(
        default=attr.Factory(lambda self: type(self).NAME, takes_self=True))

    domain: str = attr.ib(
        default=attr.Factory(lambda self: type(self).DOMAIN, takes_self=True))

    group = attr.ib(
        default=attr.Factory(lambda self: type(self).GROUP, takes_self=True))

    container = attr.ib(default=attr.Factory(lambda self: type(self).CONTAINER,
                                             takes_self=True))

    cflags = attr.ib(default=attr.Factory(list))

    ldflags = attr.ib(default=attr.Factory(list))

    run_uuid = attr.ib()

    @run_uuid.default
    def __default_run_uuid(self):
        run_group = getenv("BB_DB_RUN_GROUP", None)
        if run_group:
            return uuid.UUID(run_group)
        return uuid.uuid4()

    @run_uuid.validator
    def __check_if_uuid(self, _, value):
        if not isinstance(value, uuid.UUID):
            raise TypeError("{attribute} must be a valid UUID object")

    builddir = attr.ib(default=attr.Factory(lambda self: local.path(
        str(CFG["build_dir"])) / self.experiment.name / self.id,
                                            takes_self=True))

    source = attr.ib(
        default=attr.Factory(lambda self: type(self).SOURCE, takes_self=True))

    compiler_extension = attr.ib(
        default=attr.Factory(lambda self: ext_run.WithTimeout(
            compiler.RunCompiler(self, self.experiment)),
                             takes_self=True))

    runtime_extension = attr.ib(default=None)

    def __attrs_post_init__(self):
        db.persist_project(self)

    @abstractmethod
    def run_tests(self):
        """
        Run the tests of this project.

        Clients override this method to provide customized run-time tests.

        Args:
            experiment: The experiment we run this project under
            run: A function that takes the run command.
        """

    def run(self):
        """Run the tests of this project.

        This method initializes the default environment and takes care of
        cleaning up the mess we made, after a successfull run.

        Args:
            experiment: The experiment we run this project under
        """
        from benchbuild.utils.run import (begin_run_group, end_run_group,
                                          fail_run_group)
        CFG["experiment"] = self.experiment.name
        CFG["project"] = self.NAME
        CFG["domain"] = self.DOMAIN
        CFG["group"] = self.GROUP
        CFG["db"]["run_group"] = str(self.run_uuid)

        group, session = begin_run_group(self)
        signals.handlers.register(fail_run_group, group, session)

        try:
            self.run_tests()
            end_run_group(group, session)
        except ProcessExecutionError:
            fail_run_group(group, session)
            raise
        except KeyboardInterrupt:
            fail_run_group(group, session)
            raise
        finally:
            signals.handlers.deregister(fail_run_group)

    def clean(self):
        """Clean the project build directory."""
        builddir_p = local.path(self.builddir)
        builddir_p.delete()

    def clone(self):
        """Create a deepcopy of ourself."""
        new_p = copy.deepcopy(self)
        new_p.run_uuid = uuid.uuid4()
        return new_p

    @abstractmethod
    def compile(self):
        """Compile the project."""

    def download(self, version=None):
        """Auto-generated by with_* decorators."""
        del version
        LOG.error("Not implemented.")

    @property
    def id(self):
        version_str = bb.variants.to_str(tuple(self.variant.values()))
        return f"{self.name}/{self.group}/{version_str}/{self.run_uuid}"

    def prepare(self):
        """Prepare the build diretory."""
        builddir_p = local.path(self.builddir)
        if not builddir_p.exists():
            builddir_p.mkdir()

    def redirect(self):
        """Redirect execution to a containerized benchbuild instance."""
        LOG.error("Redirection not supported by project.")


    def source_of(self, name: str) -> Optional[str]:
        """
        Retrieve source for given index name.

        Args:
            project (Project): The project to access.
            name (str): Local name of the source .

        Returns:
            (Optional[BaseSource]): A source representing this variant.
        """
        variant = self.variant
        if name in variant:
            return variant[name].owner.local
        return None

    def version_of(self, name: str) -> Optional[str]:
        """
        Retrieve source for given index name.

        Args:
            project (Project): The project to access.
            name (str): Local name of the source .

        Returns:
            (Optional[BaseSource]): A source representing this variant.
        """
        variant = self.variant
        if name in variant:
            return str(variant[name])
        return None

def __split_project_input__(project_input: str) -> Tuple[str, Optional[str]]:
    split_input = project_input.rsplit('@', maxsplit=1)
    first = split_input[0]
    second = split_input[1] if len(split_input) > 1 else None

    return (first, second)


def populate(projects_to_filter=None,
             group=None) -> Mapping[str, Tuple[Type[Project], Optional[str]]]:
    """
    Populate the list of projects that belong to this experiment.

    Args:
        projects_to_filter (list(Project)):
            List of projects we want to assign to this experiment.
            We intersect the list of projects with the list of supported
            projects to get the list of projects that belong to this
            experiment.
        group (list(str))):
            In addition to the project filter, we provide a way to filter
            whole groups.
    Returns:
        a dictionary of (project name, project class) pairs.
    """
    if projects_to_filter is None:
        projects_to_filter = []

    import benchbuild.projects as all_projects
    all_projects.discover()

    prjs = ProjectRegistry.projects
    if projects_to_filter:
        prjs = {}

        def single_version_impl(version):
            return lambda: [version]

        for filter_project in set(projects_to_filter):
            project_str, version = __split_project_input__(filter_project)
            try:
                for name, project_type in ProjectRegistry.projects.items(
                        prefix=project_str):
                    if version:
                        project_type.versions = single_version_impl(version)
                    prjs.update({name: project_type})
            except KeyError:
                pass

    if group:
        groupkeys = set(group)
        prjs = {
            name: cls
            for name, cls in prjs.items() if cls.GROUP in groupkeys
        }

    return {
        x: prjs[x]
        for x in prjs if prjs[x].DOMAIN != "debug" or x in projects_to_filter
    }
