"""
Project handling for the benchbuild study.
"""
from os import path, listdir
from abc import abstractmethod
from plumbum import local
from plumbum.cmd import mv, chmod, rm, mkdir, rmdir  # pylint: disable=E0401
from benchbuild.settings import CFG
from benchbuild.utils.db import persist_project
from benchbuild.utils.actions import Clean, Step, Run

PROJECT_BIN_F_EXT = ".bin"
PROJECT_BLOB_F_EXT = ".postproc"


class ProjectRegistry(type):
    """Registry for benchbuild projects."""

    projects = {}

    def __init__(cls, name, bases, dict):
        """Registers a project in the registry."""
        super(ProjectRegistry, cls).__init__(name, bases, dict)

        if cls.NAME is not None and cls.DOMAIN is not None:
            ProjectRegistry.projects[cls.NAME] = cls


class Project(object, metaclass=ProjectRegistry):
    """
    benchbuild's Project class.

    A project defines how run-time testing and cleaning is done for this
        IR project
    """

    NAME = None
    DOMAIN = None
    GROUP = None

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
        new_self.name = cls.NAME
        new_self.domain = cls.DOMAIN
        new_self.group = cls.GROUP
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
            self.testdir = path.join(str(CFG["test_dir"]), self.domain, group,
                                     self.name)
        else:
            self.testdir = path.join(str(CFG["test_dir"]), self.domain, self.name)

        self.cflags = []
        self.ldflags = []

        self.setup_derived_filenames()

        persist_project(self)

    def setup_derived_filenames(self):
        """ Construct all derived file names. """
        self.run_f = path.join(self.builddir, self.name)
        self.bin_f = self.run_f + PROJECT_BIN_F_EXT

    def run_tests(self, experiment):
        """
        Run the tests of this project.

        Clients override this method to provide customized run-time tests.

        Args:
            experiment: The experiment we run this project under
        """
        from benchbuild.utils.run import run
        from plumbum import local
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
        with local.cwd(self.builddir):
            with local.env(BB_USE_DATABASE=1,
                           BB_DB_RUN_GROUP=self.run_uuid,
                           BB_DOMAIN=self.domain,
                           BB_GROUP=self.group_name,
                           BB_SRC_URI=self.src_uri):

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
        pass

    @abstractmethod
    def configure(self):
        """ Configure the project. """
        pass

    @abstractmethod
    def build(self):
        """ Build the project. """
        pass

    def wrap_dynamic(self, name, runner, sprefix=None):
        """
        Wrap the binary :name with the function :runner.

        This module generates a python tool :name: that can replace
        a yet unspecified binary.
        It behaves similar to the :wrap: function. However, the first
        argument is the actual binary name.

        Args:
            name: name of the python module
            runner: Function that should run the real binary
            base_class: The base_class of our project.
            base_module: The module of base_class.

        Returns: plumbum command, readty to launch.

        """
        import dill

        base_class = self.__class__.__name__
        base_module = self.__module__

        name_absolute = path.abspath(name)
        blob_f = name_absolute + PROJECT_BLOB_F_EXT
        with open(blob_f, 'wb') as blob:
            blob.write(dill.dumps(runner))

        with open(name_absolute, 'w') as wrapper:
            lines = '''#!/usr/bin/env python3
#
from benchbuild.project import Project
from benchbuild.experiment import Experiment
from plumbum import cli, local
from os import path, getenv
from benchbuild.experiment import Experiment as E
from {base_module} import {base_class} as PBC

import logging
import os
import sys
import dill

log = logging.getLogger("run")
log.setLevel(logging.ERROR)
log.addHandler(logging.StreamHandler(stream=sys.stderr))

EXPERIMENT_NAME = getenv("BB_EXPERIMENT", "unknown")
DOMAIN_NAME = getenv("BB_DOMAIN", PBC.DOMAIN)
GROUP_NAME = getenv("BB_GROUP", PBC.GROUP)

if not len(sys.argv) >= 2:
    log.error("Not enough arguments provided!\\n")
    log.error("Got: " + sys.argv + "\\n")
    sys.exit(1)

f = None
ld_library_path = "{ld_lib_path}:" + getenv("LD_LIBRARY_PATH")
RUN_F = sys.argv[1]
ARGS = sys.argv[2:]
PROJECT_NAME = path.basename(RUN_F)

if path.exists("{blobf}"):
    with local.env(BB_DB_HOST="{db_host}",
               BB_DB_PORT="{db_port}",
               BB_DB_NAME="{db_name}",
               BB_DB_USER="{db_user}",
               BB_DB_PASS="{db_pass}",
               BB_PROJECT=PROJECT_NAME,
               BB_LIKWID_DIR="{likwiddir}",
               LD_LIBRARY_PATH=ld_library_path,
               BB_CMD=RUN_F):
        with open("{blobf}", "rb") as p:
            f = dill.load(p)
        if f is not None:
            project_cls = type("Dyn_" + PROJECT_NAME, (PBC,), {{
                "NAME" : PROJECT_NAME,
                "DOMAIN" : DOMAIN_NAME,
                "GROUP" : GROUP_NAME,
                "__module__" : "__main__"
            }})

            experiment_cls = type(EXPERIMENT_NAME, (E,), {{
                "NAME" : EXPERIMENT_NAME
            }})

            e = experiment_cls([PROJECT_NAME], [GROUP_NAME])
            p = project_cls(e)

            if not sys.stdin.isatty():
                f(RUN_F, ARGS, has_stdin = True, project_name = PROJECT_NAME)
            else:
                f(RUN_F, ARGS, project_name = PROJECT_NAME)
        else:
            sys.exit(1)

    '''.format(db_host=str(CFG["db"]["host"]),
               db_port=str(CFG["db"]["port"]),
               db_name=str(CFG["db"]["name"]),
               db_user=str(CFG["db"]["user"]),
               db_pass=str(CFG["db"]["pass"]),
               likwiddir=str(CFG["likwid"]["prefix"]),
               ld_lib_path=str(CFG["ld_library_path"]).rstrip(':'),
               blobf=strip_path_prefix(blob_f, sprefix),
               base_class=base_class,
               base_module=base_module)
            wrapper.write(lines)
        chmod("+x", name_absolute)
        return local[name_absolute]


def strip_path_prefix(ipath, prefix):
    """
    Strip prefix from path.

    Args:
        ipath: input path
        prefix: the prefix to remove, if it is found in :ipath:

    Examples:
        >>> from benchbuild.project import strip_path_prefix
        >>> strip_path_prefix("/foo/bar", "/bar")
        '/foo/bar'
        >>> strip_path_prefix("/foo/bar", "/")
        'foo/bar'
        >>> strip_path_prefix("/foo/bar", "/foo")
        '/bar'
        >>> strip_path_prefix("/foo/bar", "None")
        '/foo/bar'

    """
    if prefix is None:
        return ipath

    return ipath[len(prefix):] if ipath.startswith(prefix) else ipath


def wrap(name, runner, sprefix=None):
    """ Wrap the binary :name: with the function :runner:.

    This module generates a python tool that replaces :name:
    The function in runner only accepts the replaced binaries
    name as argument. We use the cloudpickle package to
    perform the serialization, make sure :runner: can be serialized
    with it and you're fine.

    Args:
        name: Binary we want to wrap
        runner: Function that should run instead of :name:

    Returns:
        A plumbum command, ready to launch.
    """
    import dill
    from benchbuild.utils.run import run

    name_absolute = path.abspath(name)
    real_f = name_absolute + PROJECT_BIN_F_EXT
    if sprefix:
        from benchbuild.utils.run import uchroot_no_llvm as uchroot
        run(uchroot()["/bin/mv", strip_path_prefix(name_absolute, sprefix),
                               strip_path_prefix(real_f, sprefix)])
    else:
        run(mv[name_absolute, real_f])

    blob_f = name_absolute + PROJECT_BLOB_F_EXT
    with open(blob_f, 'wb') as blob:
        dill.dump(runner, blob, protocol=-1, recurse=True)

    with open(name_absolute, 'w') as wrapper:
        lines = '''#!/usr/bin/env python3
#

from plumbum import cli, local
from os import path, getenv
import sys
import dill

ld_library_path = "{ld_lib_path}:" + getenv("LD_LIBRARY_PATH")
run_f = "{runf}"
args = sys.argv[1:]
f = None
if path.exists("{blobf}"):
    with local.env(BB_DB_HOST="{db_host}",
               BB_DB_PORT="{db_port}",
               BB_DB_NAME="{db_name}",
               BB_DB_USER="{db_user}",
               BB_DB_PASS="{db_pass}",
               BB_LIKWID_DIR="{likwiddir}",
               LD_LIBRARY_PATH=ld_library_path,
               BB_CMD=run_f + " ".join(args)):
        with open("{blobf}", "rb") as p:
            f = dill.load(p)
        if f is not None:
            if not sys.stdin.isatty():
                f(run_f, args, has_stdin = True)
            else:
                f(run_f, args)
        else:
            sys.exit(1)

'''.format(db_host=str(CFG["db"]["host"]),
           db_port=str(CFG["db"]["port"]),
           db_name=str(CFG["db"]["name"]),
           db_user=str(CFG["db"]["user"]),
           db_pass=str(CFG["db"]["pass"]),
           likwiddir=str(CFG["likwid"]["prefix"]),
           ld_lib_path=str(CFG["ld_library_path"]).rstrip(':'),
           blobf=strip_path_prefix(blob_f, sprefix),
           runf=strip_path_prefix(real_f, sprefix))
        wrapper.write(lines)
    run(chmod["+x", name_absolute])
    return local[name_absolute]
