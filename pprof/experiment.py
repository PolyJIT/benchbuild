#!/usr/bin/env python
# encoding: utf-8

"""
An pprof.experiment defines a series of phases that constitute a pprof
compatible experiment. This is the default implementation of an experiment.

Clients can derive from class class::pprof.experiment.Experiment and override
the methods relvant to their experiment.

An experiment can have a variable number of phases / steps / substeps.

Phases / Steps / Substeps
-------------------------

All phases/steps/substeps support being used as a context manager. All 3 of
them catch ProcessExecutionErrors that may be thrown from plumbum, without
aborting the whole experiment. However, an error is tracked.

Actions
-------

An experiment performs the following actions in order:
    1. clean - Clean any previous runs that collide with our directory
    2. prepare - Prepare the experiment, this is a good place to copy relevant
                 files over for testing.
    3. run (run_tests) - Run the experiment. The 'meat' lies here. Override
        This to perform all your experiment needs.

"""

from plumbum import local, FG
from plumbum.cmd import mkdir, rmdir
from plumbum.commands.processes import ProcessExecutionError

from pprof.project import ProjectFactory
from pprof.settings import config
from pprof.projects import *

from contextlib import contextmanager
from os import path, listdir
from sets import Set
from pprof.utils.db import persist_experiment

import sys
import regex


def nl(o):
    """Break the current line in the stream :o:.

    Don't reuse the current line, if :o: is not attached to a tty.

    :o: the stream we break on
    :return: the stream

    """
    if o.isatty():
        o.write("\r\x1b[L")
    else:
        o.write("\n")
    return o


def to_utf8(text):
    """
    Convert given text to UTF-8 encoding (as far as possible).

    :text:
        Text object we wish to convert to utf8
    :return:
        Hopefully some text encoded in utf8, we might bail.
    """
    if not text:
        return text

    try:  # unicode or pure ascii
        return text.encode("utf8")
    except UnicodeDecodeError:
        try:  # successful UTF-8 decode means it's pretty sure UTF-8 already
            text.decode("utf8")
            return text
        except UnicodeDecodeError:
            try:  # get desperate; and yes, this has a western hemisphere bias
                return text.decode("cp1252").encode("utf8")
            except UnicodeDecodeError:
                pass

    return text  # return unchanged, hope for the best


def static_var(varname, value):
    """
    Decorate something with a static variable.

    Example:
        .. code-block:: python

            @staticvar(bar, 0)
            def foo():
                foo.bar = 1
                return foo.bar

    :varname:
        Name of the variable
    :value:
        Initial value of the static variable
    """
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate


@contextmanager
@static_var("counter", 0)
@static_var("name", "")
def phase(name, pname="FIXME: Unset"):
    """
    Introduce a new phase.

    :name:
        Name of the phase.
    """
    phase.counter += 1
    phase.name = name
    step.counter = 0

    from sys import stderr as o
    main_msg = "PHASE.{} '{}' {}".format(phase.counter, name, pname)

    nl(o).write(main_msg + " START")
    o.write("\n")
    o.flush()
    try:
        yield
        nl(o).write(main_msg + " OK")
    except (OSError, ProcessExecutionError) as e:
        try:
            o.write(to_utf8("\n" + str(e)))
        except UnicodeEncodeError:
            o.write("\nCouldn't figure out what encoding to use, sorry...")
        sys.stdout.write("\n" + main_msg + " FAILED")
    o.write("\n")
    o.flush()


@contextmanager
@static_var("counter", 0)
@static_var("name", "")
def step(name):
    """
    Introduce a new step.

    :name:
        Name of the step.
    """
    step.counter += 1
    step.name = name
    substep.counter = 0

    from sys import stderr as o
    main_msg = "    STEP.{} '{}'".format(step.counter, name)

    try:
        nl(o).write(main_msg + " START")
        yield
        nl(o).write(main_msg + " OK")
    except (OSError, ProcessExecutionError) as e:
        try:
            o.write(to_utf8("\n" + str(e)))
        except UnicodeEncodeError:
            o.write("\nCouldn't figure out what encoding to use, sorry...")
        o.write("\n" + main_msg + " FAILED")
    o.flush()


@contextmanager
@static_var("counter", 0)
@static_var("name", "")
@static_var("failed", 0)
def substep(name):
    """
    Introduce a new substep.

    :name:
        Name of the substep.
    """
    substep.counter += 1
    substep.name = name

    from sys import stdout as o
    main_msg = "        SUBSTEP.{} '{}'".format(substep.counter, name)

    nl(o).write(main_msg + " START")
    try:
        yield
        nl(o).write(main_msg + " OK")
    except (OSError, ProcessExecutionError) as e:
        try:
            o.write(to_utf8("\n" + str(e)))
        except UnicodeEncodeError:
            o.write("\nCouldn't figure out what encoding to use, sorry...")
        o.write("\n" + main_msg + "FAILED")
        o.write("\n    {} substeps have FAILED so far.".format(substep.failed))
        o.flush()
        substep.failed += 1
    o.flush()


def get_group_projects(group, experiment):
    """
    Get a list of project names for the given group.

    :group:
        The group.
    :experiment:
        The experiment we collect the supported project names for.
    :returns:
        A list of project names for the group that are supported by this
        experiment.
    """
    group = []
    projects = Experiment.projects
    for name in projects:
        p = projects[name]

        if p.group_name == group:
            group.append(name)
    return group


class Experiment(object):

    """
    A series of commands executed on a project that form an experiment.

    The default implementation should provide a sane environment for all
    derivates.

    One important task executed by the basic implementation is setting up
    the default set of projects that belong to this project.
    As every project gets registered in the ProjectFactory, the experiment
    gets a list of experiment names that work as a filter.

    """

    def setup_commands(self):
        bin_path = path.join(config["llvmdir"], "bin")

        config["path"] = bin_path + ":" + config["path"]
        config["ld_library_path"] = ":".join([
            path.join(config["llvmdir"], "lib"),
            config["ld_library_path"]
        ])

    def __init__(self, name, projects=[], group=None):
        self.name = name
        self.projects = {}
        self.setup_commands()
        self.sourcedir = config["sourcedir"]
        self.builddir = path.join(config["builddir"], name)
        self.testdir = config["testdir"]

        persist_experiment(self)
        self.populate_projects(projects, group)

    def populate_projects(self, projects_to_filter, group=None):
        """
        Populate the list of projects that belong to this experiment.

        :projects_to_filter:
            List of projects we want to assign to this experiment. We intersect
            the list of projects with the list of supported projects to get
            the list of projects that belong to this experiment.
        :group:
            In addition to the project filter, we provide a way to filter whole
            groups.
        """
        self.projects = {}
        factories = ProjectFactory.factories
        for fact_id in factories:
            project = ProjectFactory.createProject(fact_id, self)
            self.projects[project.name] = project

        if projects_to_filter:
            allkeys = Set(self.projects.keys())
            usrkeys = Set(projects_to_filter)
            self.projects = {x: self.projects[x] for x in allkeys & usrkeys}

        if group:
            self.projects = {
                k: v for k, v in self.projects.iteritems() if v.group_name == group}

    def clean_project(self, p):
        with local.env(PPROF_ENABLE=0):
            p.clean()

    def prepare_project(self, p):
        with local.env(PPROF_ENABLE=0):
            p.prepare()

    def run_project(self, p):
        with local.cwd(p.builddir):
            p.run()

    def map_projects(self, fun, p=None):
        """
        Map a function over all projects.

        :fun:
            Function that gets mapped over all projects.
        :p:
            Phase name
        """
        for project_name in self.projects:
            with phase(p, project_name):
                prj = self.projects[project_name]
                llvm_libs = path.join(config["llvmdir"], "lib")
                ld_lib_path = config["ld_library_path"] + ":" + llvm_libs
                with local.env(LD_LIBRARY_PATH=ld_lib_path,
                               PPROF_EXPERIMENT=self.name,
                               PPROF_PROJECT=prj.name):
                    fun(prj)

    def clean(self):
        """Clean the experiment."""
        self.map_projects(self.clean_project, "clean")
        if (path.exists(self.builddir)) and listdir(self.builddir) == []:
            rmdir(self.builddir)

    def prepare(self):
        """
        Prepare the experiment.

        This includes creation of a build directory and setting up the logging.
        Afterwards we call the prepare method of the project.
        """
        if not path.exists(self.builddir):
            (mkdir[self.builddir] & FG(retcode=None))

        self.map_projects(self.prepare_project, "prepare")

    def run(self):
        """
        Run the experiment on all registered projects.

        Setup the environment and call run_project method on all projects.
        """
        with local.env(PPROF_EXPERIMENT_ID=str(config["experiment"])):
            self.map_projects(self.run_project, "run")


class RuntimeExperiment(Experiment):

    """ Additional runtime only features for experiments. """

    def get_papi_calibration(self, p, calibrate_call):
        """ Get calibration values for PAPI based measurements. """
        with local.cwd(self.builddir):
            with local.env(PPROF_USE_DATABASE=0, PPROF_USE_CSV=0,
                           PPROF_USE_FILE=0):
                calib_out = calibrate_call()

        calib_pattern = regex.compile(
            'Real time per call \(ns\): (?P<val>[0-9]+.[0-9]+)')
        for line in calib_out.split('\n'):
            res = calib_pattern.search(line)
            if res:
                return res.group('val')
        return None

    def persist_calibration(self, p, cmd, calibration):
        """ Persist the result of a calibration call. """
        if calibration:
            from pprof.utils.db import create_run
            from pprof.utils import schema as s

            run, session = create_run(str(cmd), p.name, self.name, p.run_uuid)
            m = s.Metric(name="papi.calibration.time_ns", value=calibration,
                         run_id=run.id)
            session.add(m)
            session.commit()

    def persist_run(self, cmd, project_name, run_uuid, timings):
        """ Persist the run results in the database."""
        from pprof.utils import schema as s
        from pprof.utils.db import create_run

        run, session = create_run(cmd, project_name, self.name, run_uuid)

        for timing in timings:
            session.add(s.Metric(name="time.user_s", value=timing[0],
                                 run_id=run.id))
            session.add(s.Metric(name="time.system_s", value=timing[1],
                                 run_id=run.id))
            session.add(s.Metric(name="time.real_s", value=timing[2],
                                 run_id=run.id))

        session.commit()
