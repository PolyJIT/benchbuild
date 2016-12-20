"""
Project handling for the benchbuild study.
"""
import os
import sys
import warnings

from os import path, listdir
from abc import abstractmethod
from plumbum import local
from benchbuild.settings import CFG
from benchbuild.utils.cmd import mv, chmod, rm, mkdir, rmdir
from benchbuild.utils.db import persist_project
from benchbuild.utils.path import list_to_path, template_str
from benchbuild.utils.run import in_builddir, unionfs, store_config
from benchbuild.utils.container import Gentoo
from functools import partial


class ProjectRegistry(type):
    """Registry for benchbuild projects."""

    projects = {}

    def __init__(cls, name, bases, attrs):
        """Registers a project in the registry."""
        super(ProjectRegistry, cls).__init__(name, bases, attrs)

        if cls.NAME is not None and cls.DOMAIN is not None:
            ProjectRegistry.projects[cls.NAME] = cls


class ProjectDecorator(ProjectRegistry):
    """
    Decorate the interface of a project with the in_builddir decorator.

    This is just a small safety net for benchbuild users, because we make
    sure to run every project method in the project's build directory.
    """

    decorated_methods = ["build", "configure", "download", "prepare",
                         "run_tests"]

    def __init__(cls, name, bases, attrs):
        unionfs_deco = None
        if CFG["unionfs"]["enable"].value():
            image_dir = CFG["unionfs"]["image"].value()
            prefix = CFG["unionfs"]["image_prefix"].value()
            base_dir = CFG["unionfs"]["base_dir"].value()
            unionfs_deco = partial(unionfs, image_dir=image_dir,
                                   image_prefix=prefix)
        config_deco = store_config

        methods = ProjectDecorator.decorated_methods
        for k, v in attrs.items():
            if (k in methods) and hasattr(cls, k):
                wrapped_fun = v
                if unionfs_deco is not None:
                    wrapped_fun = unionfs_deco()(wrapped_fun)

                wrapped_fun = in_builddir('.')(wrapped_fun)

                if k == 'configure':
                    wrapped_fun = config_deco(wrapped_fun)
                setattr(cls, k, wrapped_fun)

        super(ProjectDecorator, cls).__init__(name, bases, attrs)


class Project(object, metaclass=ProjectDecorator):
    """
    benchbuild's Project class.

    A project defines how run-time testing and cleaning is done for this
        IR project
    """

    NAME = None
    DOMAIN = None
    GROUP = None
    VERSION = None
    SRC_FILE = None
    CONTAINER = Gentoo()

    def __new__(cls, *args, **kwargs):
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
        if cls.VERSION is None:
            warnings.warn(
                "{0} @ {1} does not define a VERSION class attribute.".format(
                    cls.__name__, cls.__module__))
        if cls.SRC_FILE is None:
            warnings.warn(
                "{0} @ {1} does not offer a source file yet.".format(
                    cls.__name__, cls.__module__))
        if cls.CONTAINER is None:
            warnings.warn(
                "{0} @ {1} does not offer a container yet.".format(
                    cls.__name__, cls.__module__))

        new_self.name = cls.NAME
        new_self.domain = cls.DOMAIN
        new_self.group = cls.GROUP
        new_self.src_file = cls.SRC_FILE
        new_self.version = cls.VERSION
        new_self.container = cls.CONTAINER
        return new_self

    def __init__(self, exp, group=None):
        """
        Setup a new project.

        Args:
            exp: The experiment this project belongs to.
            group: The group this project belongs to. This is useful for
                finding group specific test input files.
        """
        self.experiment = exp
        self.group_name = group
        self.sourcedir = path.join(str(CFG["src_dir"]), self.name)
        self.builddir = path.join(str(CFG["build_dir"]), exp.name, self.name)
        if group:
            self.testdir = path.join(
                str(CFG["test_dir"]), self.domain, group, self.name)
        else:
            self.testdir = path.join(
                str(CFG["test_dir"]), self.domain, self.name)

        self.cflags = []
        self.ldflags = []

        self.setup_derived_filenames()

        persist_project(self)

    def setup_derived_filenames(self):
        """ Construct all derived file names. """
        self.run_f = path.join(self.builddir, self.name)

    def run_tests(self, experiment):
        """
        Run the tests of this project.

        Clients override this method to provide customized run-time tests.

        Args:
            experiment: The experiment we run this project under
        """
        from benchbuild.utils.run import run
        exp = wrap(self.run_f, experiment)
        with local.cwd(self.builddir):
            run(exp)

    def run(self, experiment):
        """
        Run the tests of this project.

        This method initializes the default environment and takes care of
        cleaning up the mess we made, after a successfull run.

        Args:
            experiment: The experiment we run this project under
        """
        from benchbuild.utils.run import GuardedRunException
        from benchbuild.utils.run import (begin_run_group, end_run_group,
                                          fail_run_group)
        CFG["experiment"] = self.experiment.name
        CFG["project"] = self.NAME
        CFG["domain"] = self.DOMAIN
        CFG["group"] = self.GROUP
        CFG["version"] = self.VERSION
        CFG["use_database"] = 1
        CFG["db"]["run_group"] = str(self.run_uuid)
        with local.cwd(self.builddir):
            group, session = begin_run_group(self)
            try:
                self.run_tests(experiment)
                end_run_group(group, session)
            except GuardedRunException:
                fail_run_group(group, session)
            except KeyboardInterrupt as key_int:
                fail_run_group(group, session)
                raise key_int
            if CFG["clean"].value():
                self.clean()

    def clean(self):
        """ Clean the project build directory. """
        if path.exists(self.builddir) and listdir(self.builddir) == []:
            rmdir(self.builddir)
        elif path.exists(self.builddir) and listdir(self.builddir) != []:
            rm("-rf", self.builddir)

    @property
    def compiler_extension(self):
        """ Return the compiler extension registered to this project. """
        try:
            return self._compiler_extension
        except AttributeError:
            self._compiler_extension = None
            return self._compiler_extension

    @compiler_extension.setter
    def compiler_extension(self, func):
        """
        Set a function as compiler extension.

        Args:
            func: The compiler extension function. The minimal signature that
                is required is ::
                    f(cc, **kwargs)
                where cc is the original compiler command.

        """
        self._compiler_extension = func

    @property
    def runtime_extension(self):
        """ Return the runtime extension registered for this project. """
        try:
            return self._runtime_extension
        except AttributeError:
            self._runtime_extension = None
            return self._runtime_extension

    @runtime_extension.setter
    def runtime_extension(self, func):
        """
        Set a function as compiler extension.

        Args:
            func: The compiler extension function. The minimal signature that
                is required is ::
                    f(cc, **kwargs)
                where cc is the original compiler command.

        """
        self._runtime_extension = func

    @property
    def run_uuid(self):
        """
        Get the UUID that groups all tests for one project run.

        Args:
            create_new: Create a fresh UUID (Default: False)
        """
        from os import getenv
        from uuid import uuid4

        try:
            if self._run_uuid is None:
                self._run_uuid = getenv("BB_DB_RUN_GROUP", uuid4())
        except AttributeError:
            self._run_uuid = getenv("BB_DB_RUN_GROUP", uuid4())
        return self._run_uuid

    @run_uuid.setter
    def run_uuid(self, value):
        """
        Set a new UUID for this project.

        Args:
            value: The new value to set.
        """
        from uuid import UUID
        if isinstance(value, UUID):
            self._run_uuid = value

    def prepare(self):
        """ Prepare the build diretory. """
        if not path.exists(self.builddir):
            mkdir(self.builddir)

    @abstractmethod
    def download(self):
        """ Download the input source for this project. """

    @abstractmethod
    def configure(self):
        """ Configure the project. """

    @abstractmethod
    def build(self):
        """ Build the project. """
