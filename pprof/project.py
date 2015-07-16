#!/usr/bin/env python
# encoding: utf-8

from plumbum import local
from plumbum.cmd import rm, mkdir, rmdir
from os import path, listdir
from pprof.settings import config
from pprof.utils.db import persist_project
from abc import abstractmethod


PROJECT_BIN_F_EXT = ".bin"
PROJECT_BLOB_F_EXT = ".postproc"


class ProjectFactory:
    factories = {}

    def addFactory(fact_id, projectFactory):
        ProjectFactory.factories[fact_id] = projectFactory
    addFactory = staticmethod(addFactory)

    def createProject(fact_id, exp):
        if fact_id not in ProjectFactory.factories:
            ProjectFactory.factories[fact_id] = \
                eval(fact_id + '.Factory()')

        return ProjectFactory.factories[fact_id].create(exp)
    createProject = staticmethod(createProject)


class Project(object):

    """
    pprof's Project class.

    A project defines how run-time testing and cleaning is done for this
        IR project
    """

    def __init__(self, exp, name, domain, group=None):
        """
        Setup a new project.

        Args:
            exp: The experiment this project belongs to.
            name: The name of this project.
            domain: The domain this project belongs to, e.g. 'Scientific'
            group: The group this project belongs to. This is useful for
                finding group specific test input files.
        """
        self.experiment = exp
        self.name = name
        self.domain = domain
        self.group_name = group
        self.sourcedir = path.join(config["sourcedir"], self.name)
        self.builddir = path.join(config["builddir"], exp.name, self.name)
        if group:
            self.testdir = path.join(config["testdir"], domain, group, name)
        else:
            self.testdir = path.join(config["testdir"], domain, name)

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
        exp = wrap(self.run_f, experiment)
        exp()

    def run(self, experiment):
        """
        Run the tests of this project.

        This method initializes the default environment and takes care of
        cleaning up the mess we made, after a successfull run.

        Args:
            experiment: The experiment we run this project under
        """
        with local.cwd(self.builddir):
            with local.env(PPROF_USE_DATABASE=1,
                           PPROF_DB_RUN_GROUP=self.run_uuid,
                           PPROF_DOMAIN=self.domain,
                           PPROF_GROUP=self.group_name,
                           PPROF_SRC_URI=self.src_uri):
                self.run_tests(experiment)
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
    def run_uuid(self, create_new=False):
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
    name as argument. We use PiCloud's cloudpickle library to
    perform the serialization, make sure :runner: can be serialized
    with it and you're fine.

    Args:
        name: Binary we want to wrap
        runner: Function that should run instead of :name:

    Returns:
        A plumbum command, ready to launch.
    """
    from plumbum import local
    from plumbum.cmd import mv, chmod
    from cloud.serialization import cloudpickle as cp
    from os import path

    name_absolute = path.abspath(name)
    real_f = name_absolute + PROJECT_BIN_F_EXT
    mv(name_absolute, real_f)

    blob_f = name_absolute + PROJECT_BLOB_F_EXT
    with open(blob_f, 'wb') as b:
        b.write(cp.dumps(runner))

    with open(name_absolute, 'w') as w:
        lines = '''#!/usr/bin/env python
# encoding: utf-8

from plumbum import cli, local
from os import path
import sys
import pickle

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
            f = pickle.load(p)
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
           blobf=blob_f,
           runf=real_f)
        w.write(lines)
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
    from plumbum import local
    from plumbum.cmd import chmod
    from cloud.serialization import cloudpickle as cp
    from os import path

    name_absolute = path.abspath(name)
    blob_f = name_absolute + PROJECT_BLOB_F_EXT
    with open(blob_f, 'wb') as b:
        b.write(cp.dumps(runner))

    with open(name_absolute, 'w') as w:
        lines = '''#!/usr/bin/env python
# encoding: utf-8

from pprof.project import Project
from pprof.experiment import Experiment
from plumbum import cli, local
from os import path, getenv
import sys
import pickle

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
            f = pickle.load(p)
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
        w.write(lines)
    chmod("+x", name_absolute)
    return local[name_absolute]
