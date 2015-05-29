#!/usr/bin/env python
# encoding: utf-8

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

    :o: the stream we break on
    :return: the stream

    """

    if o.isatty():
        o.write("\r\x1b[L")
    else:
        o.write("\n")
    return o


def to_utf8(text):
    """Convert given text to UTF-8 encoding (as far as possible)."""
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
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate


@contextmanager
@static_var("counter", 0)
@static_var("name", "")
def phase(name):
    phase.counter += 1
    phase.name = name
    step.counter = 0

    from sys import stderr as o

    nl(o).write("PHASE.{} '{}' START".format(phase.counter, name))
    o.flush()
    try:
        yield
    except (OSError, ProcessExecutionError) as e:
        o.write("\n" + to_utf8(str(e)))
        sys.stdout.write("\nPHASE.{} '{}' FAILED".format(phase.counter, name))
        raise e
    o.write(
        "\r\x1b[KPHASE.{} '{}' OK".format(phase.counter, name))
    o.flush()


@contextmanager
@static_var("counter", 0)
@static_var("name", "")
def step(name):
    step.counter += 1
    step.name = name
    substep.counter = 0

    from sys import stderr as o

    nl(o).write("PHASE.{} '{}' STEP.{} '{}' START".format(
        phase.counter, phase.name, step.counter, name))
    o.flush()
    try:
        yield
    except (OSError, ProcessExecutionError) as e:
        o.write("\n" + to_utf8(str(e)))
        o.write("\nPHASE.{} '{}' STEP.{} '{}' FAILED".format(
            phase.counter, phase.name, step.counter, name))
        raise e
    nl(o).write("PHASE.{} '{}' STEP.{} '{}' OK".format(
        phase.counter, phase.name, step.counter, name))
    o.flush()


@contextmanager
@static_var("counter", 0)
@static_var("name", "")
@static_var("failed", 0)
def substep(name):
    substep.counter += 1
    substep.name = name

    from sys import stdout as o

    nl(o).write("PHASE.{} '{}' STEP.{} '{}' SUBSTEP.{} '{}' START".format(
        phase.counter, phase.name, step.counter, step.name, substep.counter, name))
    o.flush()
    try:
        yield
    except (OSError, ProcessExecutionError) as e:
        o.write("\n" + to_utf8(str(e)))
        o.write("\nPHASE.{} '{}' STEP.{} '{}' SUBSTEP.{} '{}' FAILED".format(
            phase.counter, phase.name, step.counter, step.name, substep.counter, name))
        o.write("\n{} substeps have FAILED so far.".format(substep.failed))
        o.flush()
        substep.failed += 1
        raise e
    nl(o).write("PHASE.{} '{}' STEP.{} '{}' SUBSTEP.{} '{}' OK".format(
        phase.counter, phase.name, step.counter, step.name, substep.counter, name))
    o.flush()


def synchronize_project_with_db(p):
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


def try_catch_log(func):
    def try_catch_func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ProcessExecutionError as e:
            LOG.error("error while executing command in " + func.__name__)
            LOG.error(unicode(e))
            LOG.error(e.message)
            if len(e.stdout) > 0:
                LOG.error("\n   |".join(e.stdout.splitlines()))
            if len(e.stderr) > 0:
                LOG.error("\n   |".join(e.stderr.splitlines()))
        except Exception as e:
            LOG.error("error in " + func.__name__)
            LOG.error("  args   : " + str(args))
            LOG.error("  kwargs : " + str(kwargs))
            LOG.error(unicode(e))
        except KeyboardInterrupt as kb:
            LOG.error("keyboard interrupt in " + func.__name__)
            LOG.error("  args   : " + str(args))
            LOG.error("  kwargs : " + str(kwargs))
            LOG.error(
                "FIXME: Cleanup after user interruption not implemented!")
            raise
    return try_catch_func_wrapper


def get_group_projects(group, experiment):
    """Get a list of project names for the given group

    :group: TODO
    :experiment: TODO
    :returns: TODO

    """
    from pprof.experiment import Experiment

    group = []
    projects = Experiment.projects
    for name in projects:
        p = projects[name]

        if p.group_name == group:
            group.append(name)
    return group


class Experiment(object):

    """ An series of commands executed on a project that form an experiment """

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

    @try_catch_log
    def clean_project(self, p):
        p.clean()

    def clean(self):
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

    @try_catch_log
    def prepare_project(self, p):
        p.prepare()

    def prepare(self):
        if not path.exists(self.builddir):
            mkdir[self.builddir] & FG(retcode=None)

        # Setup experiment logger
        handler = logging.FileHandler(self.error_f)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(FORMATTER)
        LOG.addHandler(handler)

        self.map_projects(self.prepare_project, "prepare")

    @try_catch_log
    def run_project(self, p):
        with local.cwd(p.builddir):
            p.run()

    def run(self):
        """Run the experiment on all registered projects
        """
        with local.env(PPROF_EXPERIMENT_ID=str(config["experiment"])):
            self.map_projects(self.run_project, "run")

    @classmethod
    def parse_result(cls, report, prefix, project_block):
        """
        Parse a given project result block into a dictionary. We take a
        report dictionary that assigns a fieldname to a regex with at most 1
        matchgroup.

        :report: The report we should parse out of this project block.
        :prefix: An existing dictionary to work with
        :project_block: A string region, taken from an arbitrary result file
        :return: A dictionary of name-value pairs
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
        """
        pass

    def collect_results(self):
        """Collect all project-specific results into one big result file for
        further processing. Later processing steps might have to regain
        per-project information from this file again.
        :returns: TODO

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
