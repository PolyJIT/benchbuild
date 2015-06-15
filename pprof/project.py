#!/usr/bin/env python
# encoding: utf-8

from plumbum import local
from plumbum.cmd import rm, mkdir, rmdir
from os import path, listdir
from pprof.settings import config
from pprof.utils.db import persist_project
from abc import abstractmethod

import sys
import logging

# Configure the log
HANDLER = logging.StreamHandler(sys.stdout)
HANDLER.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s :: %(message)s'))

LOG = logging.getLogger(__name__)
LOG.addHandler(HANDLER)

PROJECT_LIKWID_F_EXT = ".txt"
PROJECT_BIN_F_EXT = ".bin"
PROJECT_BLOB_F_EXT = ".postproc"
PROJECT_TIME_F_EXT = ".time"
PROJECT_CALLS_F_EXT = ".calls"
PROJECT_RESULT_F_EXT = ".result"
PROJECT_CALIB_CALLS_F_EXT = ".calibrate.calls"
PROJECT_CALIB_PROFILE_F_EXT = ".calibrate.profile.out"


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

    """ A project defines how run-time testing and cleaning is done for this
        IR project
    """

    def __init__(self, exp, name, domain, group=None):
        self.experiment = exp
        self.name = name
        self.domain = domain
        self.group_name = group
        self.src_uri = ""

        self.sourcedir = path.join(config["sourcedir"], self.name)
        self.builddir = path.join(config["builddir"], exp.name, self.name)
        if group:
            self.testdir = path.join(config["testdir"], domain, group, name)
        else:
            self.testdir = path.join(config["testdir"], domain, name)

        self.inputs = set()
        self.outputs = set()

        self.products = set()
        self.cflags = []
        self.ldflags = []

        self.setup_derived_filenames()

        persist_project(self)

    def setup_derived_filenames(self):
        self.run_f = path.join(self.builddir, self.name)
        self.result_f = self.run_f + PROJECT_RESULT_F_EXT
        self.bin_f = self.run_f + PROJECT_BIN_F_EXT
        self.time_f = self.run_f + PROJECT_TIME_F_EXT
        self.calibrate_calls_f = self.run_f + PROJECT_CALIB_CALLS_F_EXT
        self.calls_f = path.join(self.builddir, "papi.calls.out")
        self.likwid_f = self.run_f + PROJECT_LIKWID_F_EXT

        self.products.clear()
        self.products.add(self.run_f)
        self.products.add(self.bin_f)
        self.products.add(self.time_f)
        self.products.add(self.likwid_f)
        self.products.add(self.calls_f)
        self.products.add(self.result_f)

    def run_tests(self, experiment):
        exp = wrap(self.run_f, experiment)
        exp()

    run_uuid = None

    def run(self, experiment):
        from uuid import uuid4
        with local.cwd(self.builddir):
            if self.run_uuid is None:
                self.run_uuid = uuid4()
            with local.env(PPROF_USE_DATABASE=1,
                           PPROF_DB_RUN_GROUP=self.run_uuid,
                           PPROF_DOMAIN=self.domain,
                           PPROF_GROUP=self.group_name,
                           PPROF_SRC_URI=self.src_uri):
                self.run_tests(experiment)

    def clean(self):
        dirs_to_remove = set([])

        for product in self.products:
            if path.exists(product) and not path.isdir(product):
                rm(product)
            elif path.isdir(product):
                dirs_to_remove.add(product)

        for dir_to_rm in dirs_to_remove:
            if listdir(dir_to_rm) == []:
                rmdir(dir_to_rm)

        if path.exists(self.builddir) and listdir(self.builddir) == []:
            rmdir(self.builddir)
        elif path.exists(self.builddir) and listdir(self.builddir) != []:
            LOG.warn(self.name + " project unclean, force removing " +
                     self.builddir)
            rm("-rf", self.builddir)

    def prepare(self):
        if not path.exists(self.builddir):
            mkdir(self.builddir)

    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def configure(self):
        pass

    @abstractmethod
    def build(self):
        pass


def wrap(name, runner):
    """Wrap the binary :name: with the function :runner:.

    This module generates a python tool that replaces :name:
    The function in runner only accepts the replaced binaries
    name as argument. We use PiCloud's cloudpickle library to
    perform the serialization, make sure :runner: can be serialized
    with it and you're fine.

    :name: Binary we want to wrap
    :runner: Function that should run instead of :name:
    :returns: plumbum command, readty to launch.

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
    with open("{blobf}", "rb") as p:
        f = pickle.load(p)
    with local.env(PPROF_DB_HOST="{db_host}",
               PPROF_DB_PORT="{db_port}",
               PPROF_DB_NAME="{db_name}",
               PPROF_DB_USER="{db_user}",
               PPROF_DB_PASS="{db_pass}",
               PPROF_CMD=run_f + " ".join(args)):
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
           blobf=blob_f,
           runf=real_f)
        w.write(lines)
    chmod("+x", name_absolute)
    return local[name_absolute]


def wrap_dynamic(name, runner):
    """Wrap the binary :name: with the function :runner:.

    This module generates a python tool :name: that can replace
    a yet unspecified binary.
    It behaves similar to the :wrap: function. However, the first
    argument is the actual binary name.

    :name: name of the python module
    :runner: Function that should run the real binary
    :returns: plumbum command, readty to launch.

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
    with open("{blobf}", "rb") as p:
        f = pickle.load(p)
    with local.env(PPROF_DB_HOST="{db_host}",
               PPROF_DB_PORT="{db_port}",
               PPROF_DB_NAME="{db_name}",
               PPROF_DB_USER="{db_user}",
               PPROF_DB_PASS="{db_pass}",
               PPROF_PROJECT=project_name,
               PPROF_CMD=run_f):
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
           blobf=blob_f)
        w.write(lines)
    chmod("+x", name_absolute)
    return local[name_absolute]
