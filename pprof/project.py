"""
Project handling for the pprof study.
"""
from os import path, listdir
from abc import abstractmethod
from plumbum import local
from plumbum.cmd import mv, chmod, rm, mkdir, rmdir  # pylint: disable=E0401
from pprof.settings import config
from pprof.utils.db import persist_project

PROJECT_BIN_F_EXT = ".bin"
PROJECT_BLOB_F_EXT = ".postproc"


class ProjectRegistry(type):
    """Registry for pprof projects."""

    projects = {}

    def __init__(cls, name, bases, dict):
        """Registers a project in the registry."""
        super(ProjectRegistry, cls).__init__(name, bases, dict)

        if cls.NAME is not None and cls.DOMAIN is not None:
            ProjectRegistry.projects[cls.NAME] = cls


class Project(object, metaclass=ProjectRegistry):
    """
    pprof's Project class.

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
                "{} @ {} does not define a NAME class attribute.".format(
                    cls.__name__, cls.__module__))
        if cls.DOMAIN is None:
            raise AttributeError(
                "{} @ {} does not define a DOMAIN class attribute.".format(
                    cls.__name__, cls.__module__))
        if cls.GROUP is None:
            raise AttributeError(
                "{} @ {} does not define a GROUP class attribute.".format(
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
        self.sourcedir = path.join(config["sourcedir"], self.name)
        self.builddir = path.join(config["builddir"], exp.name, self.name)
        if group:
            self.testdir = path.join(config["testdir"], self.domain, group,
                                     self.name)
        else:
            self.testdir = path.join(config["testdir"], self.domain, self.name)

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
        from pprof.utils.run import run
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
        from pprof.utils.run import GuardedRunException
        from pprof.utils.run import (begin_run_group, end_run_group,
                                     fail_run_group)
        with local.cwd(self.builddir):
            with local.env(PPROF_USE_DATABASE=1,
                           PPROF_DB_RUN_GROUP=self.run_uuid,
                           PPROF_DOMAIN=self.domain,
                           PPROF_GROUP=self.group_name,
                           PPROF_SRC_URI=self.src_uri):

                group, session = begin_run_group(self)
                try:
                    self.run_tests(experiment)
                    end_run_group(group, session)
                except GuardedRunException:
                    fail_run_group(group, session)
                except KeyboardInterrupt as key_int:
                    fail_run_group(group, session)
                    raise key_int
        if not config["keep"]:
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
                self._run_uuid = getenv("PPROF_DB_RUN_GROUP", uuid4())
        except AttributeError:
            self._run_uuid = getenv("PPROF_DB_RUN_GROUP", uuid4())
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


def wrap(name, runner):
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

    name_absolute = path.abspath(name)
    real_f = name_absolute + PROJECT_BIN_F_EXT
    mv(name_absolute, real_f)

    blob_f = name_absolute + PROJECT_BLOB_F_EXT
    with open(blob_f, 'wb') as blob:
        dill.dump(runner, blob, protocol=-1, recurse=True)

    with open(name_absolute, 'w') as wrapper:
        lines = '''#!/usr/bin/env python3
#

from plumbum import cli, local
from os import path
import sys
import dill

run_f = "{runf}"
args = sys.argv[1:]
f = None
if path.exists("{blobf}"):
    with local.env(PPROF_DB_HOST="{db_host}",
               PPROF_DB_PORT="{db_port}",
               PPROF_DB_NAME="{db_name}",
               PPROF_DB_USER="{db_user}",
               PPROF_DB_PASS="{db_pass}",
               PPROF_LIKWID_DIR="{likwiddir}",
               LD_LIBRARY_PATH="{ld_lib_path}",
               PPROF_CMD=run_f + " ".join(args)):
        with open("{blobf}", "rb") as p:
            f = dill.load(p)
        if f is not None:
            if not sys.stdin.isatty():
                f(run_f, args, has_stdin = True)
            else:
                f(run_f, args)
        else:
            sys.exit(1)

'''.format(db_host=config["db_host"],
           db_port=config["db_port"],
           db_name=config["db_name"],
           db_user=config["db_user"],
           db_pass=config["db_pass"],
           likwiddir=config["likwiddir"],
           ld_lib_path=config["ld_library_path"],
           blobf=path.relpath(blob_f),
           runf=path.relpath(real_f))
        wrapper.write(lines)
    chmod("+x", name_absolute)
    return local[name_absolute]


def wrap_dynamic(name, runner):
    """
    Wrap the binary :name with the function :runner.

    This module generates a python tool :name: that can replace
    a yet unspecified binary.
    It behaves similar to the :wrap: function. However, the first
    argument is the actual binary name.

    Args:
        name: name of the python module
        runner: Function that should run the real binary

    Returns: plumbum command, readty to launch.

    """
    import dill

    name_absolute = path.abspath(name)
    blob_f = name_absolute + PROJECT_BLOB_F_EXT
    with open(blob_f, 'wb') as blob:
        blob.write(dill.dumps(runner))

    with open(name_absolute, 'w') as wrapper:
        lines = '''#!/usr/bin/env python3
#

from pprof.project import Project
from pprof.experiment import Experiment
from plumbum import cli, local
from os import path, getenv
import sys
import dill

if not len(sys.argv) >= 2:
    os.stderr.write("Not enough arguments provided!\\n")
    os.stderr.write("Got: " + sys.argv + "\\n")
    sys.exit(1)

f = None
run_f = sys.argv[1]
args = sys.argv[2:]
project_name = path.basename(run_f)
if path.exists("{blobf}"):
    with local.env(PPROF_DB_HOST="{db_host}",
               PPROF_DB_PORT="{db_port}",
               PPROF_DB_NAME="{db_name}",
               PPROF_DB_USER="{db_user}",
               PPROF_DB_PASS="{db_pass}",
               PPROF_PROJECT=project_name,
               PPROF_LIKWID_DIR="{likwiddir}",
               LD_LIBRARY_PATH="{ld_lib_path}",
               PPROF_CMD=run_f):
        with open("{blobf}", "rb") as p:
            f = dill.load(p)
        if f is not None:
            exp_name = getenv("PPROF_EXPERIMENT", "unknown")
            domain_name = getenv("PPROF_DOMAIN", "unknown")
            group_name = getenv("PPROF_GROUP", "unknwon")
            e = Experiment(exp_name, [], group_name)
            p = Project(e, project_name, domain_name, group_name)

            if not sys.stdin.isatty():
                f(run_f, args, has_stdin = True, project_name = project_name)
            else:
                f(run_f, args, project_name = project_name)
        else:
            sys.exit(1)

'''.format(db_host=config["db_host"],
           db_port=config["db_port"],
           db_name=config["db_name"],
           db_user=config["db_user"],
           db_pass=config["db_pass"],
           likwiddir=config["likwiddir"],
           ld_lib_path=config["ld_library_path"],
           blobf=blob_f)
        wrapper.write(lines)
    chmod("+x", name_absolute)
    return local[name_absolute]
