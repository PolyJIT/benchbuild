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
import uuid
from abc import abstractmethod
from functools import partial
from os import getenv, listdir, path

import attr
from plumbum import ProcessExecutionError, local
from pygtrie import StringTrie

import benchbuild.extensions as ext
import benchbuild.signals as signals
import benchbuild.utils.run as ur
from benchbuild.settings import CFG
from benchbuild.utils.cmd import mkdir, rm, rmdir
from benchbuild.utils.container import Gentoo
from benchbuild.utils.db import persist_project
from benchbuild.utils.run import in_builddir, store_config, unionfs
from benchbuild.utils.versions import get_version_from_cache_dir
from benchbuild.utils.wrapping import wrap

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

    decorated_methods = [
        "build", "configure", "download", "prepare", "run_tests"
    ]

    def __init__(cls, name, bases, attrs):
        unionfs_deco = None
        if CFG["unionfs"]["enable"].value():
            image_dir = CFG["unionfs"]["image"].value()
            prefix = CFG["unionfs"]["image_prefix"].value()
            unionfs_deco = partial(
                unionfs, image_dir=image_dir, image_prefix=prefix)
        config_deco = store_config

        methods = ProjectDecorator.decorated_methods
        for key, value in attrs.items():
            if (key in methods) and hasattr(cls, key):
                wrapped_fun = value
                if key == 'configure':
                    wrapped_fun = config_deco(wrapped_fun)

                if unionfs_deco is not None:
                    wrapped_fun = unionfs_deco()(wrapped_fun)

                wrapped_fun = in_builddir('.')(wrapped_fun)
                setattr(cls, key, wrapped_fun)

        super(ProjectDecorator, cls).__init__(name, bases, attrs)


@attr.s
class Project(object, metaclass=ProjectDecorator):
    """Abstract class for benchbuild projects.

    A project is an arbitrary software system usable by benchbuild in
    experiments.
    Subclasses of Project are registered automatically by benchbuild, if
    imported in the same interpreter session. For this to happen, you must list
    the in the settings under plugins -> projects.

    A project implementation *must* provide the following methods:
        download: Download the sources into the build directory.
        configure: Configure the sources, replace the compiler with our wrapper,
            if possible.
        build: Build the sources, with the wrapper compiler.

    A project implementation *may* provide the following functions:
        run_tests: Wrap any binary that has to be run under the
            runtime_extension wrapper and execute an implementation defined
            set of run-time tests.
            Defaults to a call of a binary with the name `run_f` in the
            build directory without arguments.
        prepare: Prepare the project's build directory. Defaults to a
            simple call to 'mkdir'.
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
        src_file (str, optional):
            A main src_file this project is assigned to. Defaults to `SRC_FILE`
        container (benchbuild.utils.container.Container, optional):
            A uchroot compatible container that we can use for this project.
            Defaults to `benchbuild.utils.container.Gentoo`.
        version (str, optional):
            A version information for this project. Defaults to `VERSION`.
        builddir (str, optional):
            The build directory for this project. Auto generated, if not set.
        testdir (str, optional):
            The location of any additional test-files for this project,
            usually stored out of tree. Auto generated, if not set. Usually a
            project implementation
            will define this itself.
        cflags (:obj:`list` of :obj:`str`, optional)
            A list of cflags used, for compilation of this project.
        ldflags (:obj:`list` of :obj:`str`, optional)
            A list of ldflags used, for compilation of this project.
        run_f (str, optional):
            A filename that points to the binary we want to track.
            Usually a project implementation will define this itself.
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
    NAME = None
    DOMAIN = None
    GROUP = None
    VERSION = None
    SRC_FILE = None

    def __new__(cls, *_):
        """Create a new project instance and set some defaults."""
        new_self = super(Project, cls).__new__(cls)
        if cls.NAME is None:
            raise AttributeError(
                "{0} @ {1} does not define a NAME class attribute.".format(
                    cls.__name__, cls.__module__))
        if cls.DOMAIN is None:
            raise AttributeError(
                "{0} @ {1} does not define a DOMAIN class attribute.".format(
                    cls.__name__, cls.__module__))
        if cls.GROUP is None:
            raise AttributeError(
                "{0} @ {1} does not define a GROUP class attribute.".format(
                    cls.__name__, cls.__module__))
        return new_self

    experiment = attr.ib()

    name = attr.ib(
        default=attr.Factory(lambda self: type(self).NAME, takes_self=True))

    domain = attr.ib(
        default=attr.Factory(lambda self: type(self).DOMAIN, takes_self=True))

    group = attr.ib(
        default=attr.Factory(lambda self: type(self).GROUP, takes_self=True))

    src_file = attr.ib(
        default=attr.Factory(
            lambda self: type(self).SRC_FILE, takes_self=True))

    container = attr.ib(default=Gentoo())

    version = attr.ib(
        default=attr.Factory(
            lambda self: get_version_from_cache_dir(self.src_file),
            takes_self=True))

    builddir = attr.ib(default=attr.Factory(
        lambda self: path.join(
            str(CFG["build_dir"]),
            "{0}-{1}-{2}-{3}".format(self.experiment.name,
                                     self.name, self.group,
                                     self.experiment.id)),
        takes_self=True))

    testdir = attr.ib()

    @testdir.default
    def __default_testdir(self):
        if self.group:
            return path.join(
                str(CFG["test_dir"]), self.domain, self.group, self.name)
        else:
            return path.join(str(CFG["test_dir"]), self.domain, self.name)

    cflags = attr.ib(default=attr.Factory(list))

    ldflags = attr.ib(default=attr.Factory(list))

    run_f = attr.ib(
        default=attr.Factory(
            lambda self: path.join(self.builddir, self.name), takes_self=True))

    run_uuid = attr.ib()

    @run_uuid.default
    def __default_run_uuid(self):
        return getenv("BB_DB_RUN_GROUP", uuid.uuid4())

    @run_uuid.validator
    def __check_if_uuid(self, _, value):
        if not isinstance(value, uuid.UUID):
            raise TypeError("{attribute} must be a valid UUID object")

    compiler_extension = attr.ib(default=attr.Factory(
        lambda self: ext.RunWithTimeout(
            ext.RunCompiler(self, self.experiment)), takes_self=True))

    runtime_extension = attr.ib(default=None)

    def __attrs_post_init__(self):
        persist_project(self)

    def run_tests(self, runner):
        """
        Run the tests of this project.

        Clients override this method to provide customized run-time tests.

        Args:
            experiment: The experiment we run this project under
            run: A function that takes the run command.
        """
        exp = wrap(self.run_f, self)
        runner(exp)

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
        CFG["version"] = self.VERSION
        CFG["db"]["run_group"] = str(self.run_uuid)
        with local.cwd(self.builddir):
            group, session = begin_run_group(self)
            signals.handlers.register(fail_run_group, group, session)

            try:
                self.run_tests(ur.run)
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
        if path.exists(self.builddir) and listdir(self.builddir) == []:
            rmdir(self.builddir)
        elif path.exists(self.builddir) and listdir(self.builddir) != []:
            rm("-rf", self.builddir)

    def prepare(self):
        """Prepare the build diretory."""
        if not path.exists(self.builddir):
            mkdir(self.builddir)

    @abstractmethod
    def download(self):
        """Download the input source for this project."""

    @abstractmethod
    def configure(self):
        """Configure the project."""

    @abstractmethod
    def build(self):
        """Build the project."""

    def clone(self):
        """Create a deepcopy of ourself."""
        new_p = copy.deepcopy(self)
        new_p.run_uuid = uuid.uuid4()
        return new_p

    @property
    def id(self):
        return "{name}-{group}-{id}".format(
            name=self.name, group=self.group, id=self.run_uuid)

def populate(projects_to_filter=None, group=None):
    """
    Populate the list of projects that belong to this experiment.

    Args:
        projects_to_filter (list(Project)):
            List of projects we want to assign to this experiment.
            We intersect the list of projects with the list of supported
            projects to get the list of projects that belong to this
            experiment.
        group (list(str)):
            In addition to the project filter, we provide a way to filter
            whole groups.
    """
    if projects_to_filter is None:
        projects_to_filter = []

    import benchbuild.projects as all_projects
    all_projects.discover()

    prjs = ProjectRegistry.projects
    if projects_to_filter:
        prjs = {}
        for filter_project in set(projects_to_filter):
            try:
                prjs.update({x: y for x, y in
                             ProjectRegistry.projects.items(prefix=filter_project)})
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
