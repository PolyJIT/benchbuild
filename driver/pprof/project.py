#!/usr/bin/env python
# encoding: utf-8

from plumbum import FG, local
from plumbum.commands import ProcessExecutionError
from plumbum.cmd import find, echo, rm, mkdir, rmdir, cp, ln, cat, make, chmod

from os import path, listdir
from glob import glob
from functools import wraps
from pplog import log_with
from settings import config

import sys
import logging

# Configure the log
formatter = logging.Formatter('%(asctime)s - %(levelname)s :: %(message)s')

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

log = logging.getLogger(__name__)
log.addHandler(handler)

PROJECT_OPT_F_EXT = ".opt"
PROJECT_ASM_F_EXT = ".s"
PROJECT_OBJ_F_EXT = ".o"
PROJECT_TAR_F_EXT = ".tar.gz"
PROJECT_LIKWID_F_EXT = ".txt"
PROJECT_CSV_F_EXT = ".csv"
PROJECT_INST_F_EXT = ".inst"
PROJECT_BIN_F_EXT = ".bin"
PROJECT_PREOPT_F_EXT = ".preopt"
PROJECT_TIME_F_EXT = ".time"
PROJECT_PROFILE_F_EXT = ".profile.out"
PROJECT_CALLS_F_EXT = ".calls"
PROJECT_RESULT_F_EXT = ".result"
PROJECT_CALIB_CALLS_F_EXT = ".calibrate.calls"
PROJECT_CALIB_PROFILE_F_EXT = ".calibrate.profile.out"


class ProjectFactory:
    factories = {}

    def addFactory(id, projectFactory):
        ProjectFactory.factories[id] = projectFactory
    addFactory = staticmethod(addFactory)

    def createProject(id, exp):
        if not ProjectFactory.factories.has_key(id):
            ProjectFactory.factories[id] = \
                eval(id + '.Factory()')
            return ProjectFactory.factories[id].create(self, exp)
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

    def setup_derived_filenames(self):
        self.base_f = path.join(self.sourcedir, self.name + ".bc")
        self.run_f = path.join(self.builddir, self.name)
        self.result_f = self.run_f + PROJECT_RESULT_F_EXT
        self.optimized_f = self.run_f + PROJECT_OPT_F_EXT
        self.asm_f = self.run_f + PROJECT_ASM_F_EXT
        self.obj_f = self.run_f + PROJECT_OBJ_F_EXT
        self.bin_f = self.run_f + PROJECT_BIN_F_EXT
        self.time_f = self.run_f + PROJECT_TIME_F_EXT
        self.calibrate_prof_f = self.run_f + PROJECT_CALIB_PROFILE_F_EXT
        self.calibrate_calls_f = self.run_f + PROJECT_CALIB_CALLS_F_EXT
        self.profbin_f = self.bin_f + PROJECT_PROFILE_F_EXT
        self.csv_f = self.run_f + PROJECT_CSV_F_EXT
        self._prof_f = self.run_f + PROJECT_PROFILE_F_EXT
        self._calls_f = self.run_f + PROJECT_CALLS_F_EXT
        self.likwid_f = self.run_f + PROJECT_LIKWID_F_EXT

        self.products.clear()
        self.products.add(self.run_f)
        self.products.add(self.optimized_f)
        self.products.add(self.bin_f)
        self.products.add(self.time_f)
        self.products.add(self.profbin_f)
        self.products.add(self.prof_f)
        self.products.add(self.likwid_f)
        self.products.add(self.csv_f)
        self.products.add(self.calls_f)
        self.products.add(self.result_f)
        self.products.add(self.asm_f)
        self.products.add(self.obj_f)

    def get_file_content(self, ifile):
        lines = []
        if path.exists(ifile):
            with open(ifile) as f:
                lines = "".join(f.readlines()).strip().split()
        return lines

    def input(self, filename):
        self.inputs.add(filename)
        return filename

    def output(self, filename):
        self.outputs.add(filename)
        return filename

    @property
    def prof_f(self):
        return self._prof_f

    @prof_f.setter
    def prof_f(self, value):
        old = self.prof_f
        self._prof_f = value
        if old in self.products:
            self.products.remove(old)
        self.products.add(value)

    @property
    def calls_f(self):
        return self._calls_f

    @calls_f.setter
    def calls_f(self, value):
        old = self.calls_f
        self._calls_f = value
        self.products.remove(old)
        self.products.add(value)

    @property
    def ld_flags(self):
        ldflags = path.join(self.sourcedir, self.name + ".pprof")
        return self.get_file_content(ldflags)

    @property
    def polli_flags(self):
        polliflags = path.join(self.sourcedir, self.name + ".polli")
        return self.get_file_content(polliflags)

    @log_with(log)
    def run_tests(self, experiment):
        exp = experiment(self.run_f)
        experiment & FG

    run_uuid = None

    @log_with(log)
    def run(self, experiment):
        import uuid
        with local.cwd(self.builddir):
            if self.run_uuid is None:
                self.run_uuid = uuid.uuid4()
            with local.env(PPROF_CMD=str(experiment(self.run_f)),
                           PPROF_USE_DATABASE=1,
                           PPROF_DB_RUN_GROUP=self.run_uuid):
                print self.run_uuid
                self.run_tests(experiment)

    @log_with(log)
    def clean(self):
        dirs_to_remove = set([])

        for product in self.products:
            if path.exists(product) and not path.isdir(product):
                rm[product] & FG
            elif path.isdir(product):
                dirs_to_remove.add(product)

        for d in dirs_to_remove:
            if listdir(d) == []:
                rmdir[d] & FG

        if path.exists(self.builddir) and listdir(self.builddir) == []:
            rmdir[self.builddir] & FG
        elif path.exists(self.builddir) and listdir(self.builddir) != []:
            log.warn(self.name + " project unclean, force removing " +
                     self.builddir)
            rm["-rf", self.builddir] & FG

    @log_with(log)
    def prepare(self):
        if not path.exists(self.builddir):
            mkdir[self.builddir] & FG

    def print_result_header(self):
        (echo["---------------------------------------------------------------"]
            >> self.result_f) & FG
        (echo[">>> ========= " + self.name + " Program"]
            >> self.result_f) & FG
        (echo["---------------------------------------------------------------"]
            >> self.result_f) & FG

        def download(self):
            pass

        def configure(self):
            pass

        def build(self):
            pass


def wrap_tool(name, wrap_with):
    from plumbum.cmd import mv
    from os import path

    if path.exists(name):
        log.error("{} still exists, move it away and:\n".format(name))
        log.error(" 1. 'run_f': to the binary you moved away\n")
        log.error(" 2. build your experiment based on run_f as before\n")
        log.error(" 3. wrap the tool with the _old_ value of 'run_f'")
        return False

    with open(name, 'w') as wrapper:
        povray.write("#!/bin/sh\n")
        povray.write(str(wrap_with) + " \"$@\"")
    return True


def print_libtool_sucks_wrapper(filepath, flags_to_hide, compiler_to_call):
    from plumbum.cmd import chmod
    with open(filepath, 'w') as wrapper:
        wrapper.writelines(
            [
                "#!/bin/sh\n",
                'FLAGS="' + " ".join(flags_to_hide) + '"\n',
                compiler_to_call + " $FLAGS $*\n"
            ]
        )
    chmod("+x", filepath)


def llvm():
    return path.join(config["llvmdir"], "bin")


def llvm_libs():
    return path.join(config["llvmdir"], "lib")


def clang_cxx():
    return local[path.join(llvm(), "clang++")]


def clang():
    return local[path.join(llvm(), "clang")]
