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

All phases/steps/substeps support being used as a context manager. All 3 of them
catch ProcessExecutionErrors that may be thrown from plumbum, without
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

from plumbum import local, cli, FG
from plumbum.cmd import (cp, chmod, sed, time, echo,
                         tee, mv, touch, awk, rm, mkdir, rmdir, grep, cat)
from plumbum.commands.processes import ProcessExecutionError

from pprof import project
from pprof.project import ProjectFactory
from pprof.projects.polybench import polybench
from pprof.projects.pprof import (sevenz, bzip2, ccrypt, crafty, crocopat,
                                  ffmpeg, gzip, js, lammps, lapack, leveldb,
                                  linpack, luleshomp, lulesh, mcrypt, minisat,
                                  openssl, postgres, povray, python, ruby, sdcc,
                                  sqlite3, tcc, x264, xz)
from pprof.projects.lnt import lnt
from pprof.settings import config

from contextlib import contextmanager
from os import path, listdir
from sets import Set
from codecs import getwriter

import re
import sys
import logging
import regex

# Configure the log
FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s :: %(message)s')
HANDLER = logging.StreamHandler(sys.stdout)
HANDLER.setFormatter(FORMATTER)
LOG = logging.getLogger(__name__)
HANDLER.setLevel(LOG.getEffectiveLevel())
LOG.addHandler(HANDLER)


def nl(o):
    """Break the current line in the stream :o:

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

    try: # unicode or pure ascii
        return text.encode("utf8")
    except UnicodeDecodeError:
        try: # successful UTF-8 decode means it's pretty sure UTF-8 already
            text.decode("utf8")
            return text
        except UnicodeDecodeError:
            try: # get desperate; and yes, this has a western hemisphere bias
                return text.decode("cp1252").encode("utf8")
            except UnicodeDecodeError:
                pass

    return text # return unchanged, hope for the best


def static_var(varname, value):
    """
    Decorate something with a static variable

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


class SubStepError(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return repr(self.args)

@contextmanager
@static_var("counter", 0)
@static_var("name", "")
def phase(name):
    """
    Introduce a new phase.

    :name:
        Name of the phase.
    """

    phase.counter += 1
    phase.name = name
    step.counter = 0

    from sys import stderr as o

    nl(o).write("PHASE.{} '{}' START".format(phase.counter, name))
    o.flush()
    try:
        yield
        nl(o).write(
            "PHASE.{} '{}' OK".format(phase.counter, name))
    except (OSError, ProcessExecutionError, SubStepError) as e:
        try:
            o.write(to_utf8("\n" + str(e)))
        except UnicodeEncodeError:
            o.write("\nCouldn't figure out what encoding to use, sorry...")
        sys.stdout.write("\nPHASE.{} '{}' FAILED".format(phase.counter, name))
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

    nl(o).write("PHASE.{} '{}' STEP.{} '{}' START".format(
        phase.counter, phase.name, step.counter, name))
    try:
        yield
        nl(o).write("PHASE.{} '{}' STEP.{} '{}' OK".format(
            phase.counter, phase.name, step.counter, name))
    except (OSError, ProcessExecutionError) as e:
        try:
            o.write(to_utf8("\n" + str(e)))
        except UnicodeEncodeError:
            o.write("\nCouldn't figure out what encoding to use, sorry...")
        o.write("\nPHASE.{} '{}' STEP.{} '{}' FAILED".format(
            phase.counter, phase.name, step.counter, name))
        raise SubStepError(name, e)
    except SubStepError as e:
        raise e
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

    nl(o).write("PHASE.{} '{}' STEP.{} '{}' SUBSTEP.{} '{}' START".format(
        phase.counter, phase.name, step.counter, step.name, substep.counter, name))
    try:
        yield
        nl(o).write("PHASE.{} '{}' STEP.{} '{}' SUBSTEP.{} '{}' OK".format(
            phase.counter, phase.name, step.counter, step.name, substep.counter, name))
    except (OSError, ProcessExecutionError) as e:
        try:
            o.write(to_utf8("\n" + str(e)))
        except UnicodeEncodeError:
            o.write("\nCouldn't figure out what encoding to use, sorry...")
        o.write("\nPHASE.{} '{}' STEP.{} '{}' SUBSTEP.{} '{}' FAILED".format(
            phase.counter, phase.name, step.counter, step.name, substep.counter, name))
        o.write("\n{} substeps have FAILED so far.".format(substep.failed))
        o.flush()
        substep.failed += 1
        raise SubStepError(name, e)
    o.flush()


def synchronize_project_with_db(p):
    """
    Synchronize a project with the database. This inserts a new entry
    in the database, if it doesn't exist yet.

    :p:
        The projec we synchronize.
    """
    from pprof.settings import get_db_connection
    conn = get_db_connection()

    sql_sel = "SELECT name FROM project WHERE name=%s"
    sql_ins = "INSERT INTO project " \
              "(name, description, src_url, domain, group_name)" \
              "VALUES (%s, %s, %s, %s, %s)"
    #sql_upd = "UPDATE project SET description = %(desc)s, src_url = %(src)s " \
    #          "domain = %(domain)s, group = %(group)s" \
    #          "WHERE name = %(name)s"
    with conn.cursor() as c:
        c.execute(sql_sel, (p.name, ))
        if not c.rowcount:
            c.execute(sql_ins, [p.name, p.name, "TODO",
                                p.domain, p.group_name])

    conn.commit()


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
        config["ld_library_path"] = path.join(config["llvmdir"], "lib") + ":" +\
            config["ld_library_path"]

    def __init__(self, name, projects=[], group=None):
        self.name = name
        self.products = Set([])
        self.projects = {}
        self.setup_commands()

        self.name = name
        self.sourcedir = config["sourcedir"]
        self.builddir = path.join(config["builddir"], name)
        self.testdir = config["testdir"]
        self.result_f = path.join(self.builddir, name + ".result")
        self.error_f = path.join(self.builddir, "error.log")

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
        for id in factories:
            project = factories[id].create(self)
            synchronize_project_with_db(project)
            self.projects[project.name] = project

        if projects_to_filter:
            allkeys = Set(self.projects.keys())
            usrkeys = Set(projects_to_filter)
            self.projects = {x: self.projects[x] for x in allkeys & usrkeys}

        if group:
            self.projects = {
                k: v for k, v in self.projects.iteritems() if v.group_name == group}

    def clean_project(self, p):
        p.clean()

    def clean(self):
        """
        Cleans the experiment.
        """

        self.map_projects(self.clean_project, "clean")
        if (path.exists(self.builddir)) and listdir(self.builddir) == []:
            rmdir[self.builddir] & FG
        if path.exists(self.result_f):
            rm[self.result_f]

        calibrate_calls_f = path.join(self.builddir, "pprof-calibrate.calls")
        calibrate_prof_f = path.join(self.builddir,
                                     "pprof-calibrate.profile.out")
        if path.exists(calibrate_calls_f):
            rm[calibrate_calls_f]
            rm[calibrate_prof_f]

    def prepare_project(self, p):
        p.prepare()

    def prepare(self):
        """
        Prepare the experiment. This includes creation of a build directory
        and setting up the logging. Afterwards we call the prepare method
        of the project.
        """

        if not path.exists(self.builddir):
            mkdir[self.builddir] & FG(retcode=None)

        # Setup experiment logger
        handler = logging.FileHandler(self.error_f)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(FORMATTER)
        LOG.addHandler(handler)

        self.map_projects(self.prepare_project, "prepare")

    def run_project(self, p):
        with local.cwd(p.builddir):
            p.run()

    def run(self):
        """
        Run the experiment on all registered projects.

        Setup the environment and call run_project method on all projects.
        """
        with local.env(PPROF_EXPERIMENT_ID=str(config["experiment"])):
            self.map_projects(self.run_project, "run")

    @classmethod
    def parse_result(cls, report, prefix, project_block):
        """
        Parse a given project result block into a dictionary. We take a
        report dictionary that assigns a fieldname to a regex with at most 1
        matchgroup.

        :cls:
            The class.
        :report:
            The report we should parse out of this project block.
        :prefix:
            An existing dictionary to work with
        :project_block:
            A string region, taken from an arbitrary result file
        :return:
            A dictionary of name-value pairs
        """
        res = prefix
        for key in report:
            res[key] = "NaN"

        for key, val in report.iteritems():
            mval = re.search(val, project_block)
            if mval is not None:
                res[key] = mval.group(1)

        return res

    def generate_report(self, perf_project_results):
        """
        Provide users with per project results in the form of a dictionary:
            [{ "<project_name>": "project payload" },...]
        Let users do what they want with it.

        :perf_project_results:
            TODO
        :return:
            TODO
        """
        pass

    def collect_results(self):
        """
        Collect all project-specific results into one big result file for
        further processing. Later processing steps might have to regain
        per-project information from this file again.

        :return:
            TODO
        """
        result_files = Set([])
        for project_name in self.projects:
            prj = self.projects[project_name]
            print prj.result_f
            if path.exists(prj.result_f):
                result_files.add(prj.result_f)

        if len(result_files) > 0:
            prep_cat = cat
            for res in result_files:
                prep_cat = prep_cat[res]
            prep_cat = (prep_cat > self.result_f)
            prep_cat & FG

        with open(self.result_f) as result_f:
            pattern = re.compile("-{63}\n>>> =+ ([-\\w]+) Program\n-{63}\n")
            file_content = result_f.read()
            split_items = pattern.split(file_content)
            split_items.pop(0)
            per_project_results = zip(*[iter(split_items)] * 2)
            self.generate_report(per_project_results)

    def map_projects(self, fun, p=None):
        for project_name in self.projects:
            with phase(p):
                prj = self.projects[project_name]
                llvm_libs = path.join(config["llvmdir"], "lib")
                ld_lib_path = config["ld_library_path"] + ":" + llvm_libs
                with local.env(LD_LIBRARY_PATH=ld_lib_path,
                               PPROF_EXPERIMENT=self.name,
                               PPROF_PROJECT=prj.name):
                    fun(prj)

    def verify_product(self, filename, log=None):
        """
        Verify if a specified product has been created by the experiment.

        :filename:
            The product we expect to exist.
        :log:
            Optional. Log any errors.
        """
        if not log:
            log = LOG

        if not path.exists(filename):
            log.error("{0} not created by project.".format(filename))


class RuntimeExperiment(Experiment):

    """ Additional runtime only features for experiments """

    def get_papi_calibration(self, p, calibrate_call):
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
