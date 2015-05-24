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

PROJECT_LIKWID_F_EXT = ".txt"
PROJECT_BIN_F_EXT = ".bin"
PROJECT_TIME_F_EXT = ".time"
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

    @log_with(log)
    def run_tests(self, experiment):
        exp = experiment(self.run_f)
        exp()

    run_uuid = None
    @log_with(log)
    def run(self, experiment):
        from uuid import uuid4
        with local.cwd(self.builddir):
            if self.run_uuid is None:
                self.run_uuid = uuid4()
            with local.env(PPROF_CMD=str(experiment(self.run_f)),
                           PPROF_USE_DATABASE=1,
                           PPROF_DB_RUN_GROUP=self.run_uuid):
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


def wrap_tool(name, wrap):
    from plumbum import local
    from plumbum.cmd import mv, chmod
    from os import path

    real_f = name + PROJECT_BIN_F_EXT
    mv(name, real_f)

    with open(name, 'w') as wrapper:
        wrapper.write("#!/bin/sh\n")
        wrapper.write(str(wrap(real_f)) + " \"$@\"")
    chmod("+x", name)
    return local["./{}".format(name)]
