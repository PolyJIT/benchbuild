#!/usr/bin/env python
# encoding: utf-8

from plumbum import local, cli, FG
from plumbum.cmd import (cp, chmod, sed, time, echo,
                         tee, mv, touch, awk, rm, mkdir, rmdir, grep, cat)
from plumbum.commands.processes import ProcessExecutionError

from pprof import project
from pprof.project import ProjectFactory

from pprof import lapack
from pprof.projects.polybench import polybench
from pprof.projects.pprof import (sevenz, bzip2, ccrypt, crafty, crocopat,
        ffmpeg, gzip, js, lammps, leveldb, linpack, luleshomp, lulesh, mcrypt,
        minisat, openssl, postgres, povray, python, ruby, sdcc, sqlite3, tcc,
        x264, xz)

from pprof.settings import config

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
            LOG.error("FIXME: Cleanup after user interruption not implemented!")
            raise
    return try_catch_func_wrapper

class Experiment(object):

    """ An series of commands executed on a project that form an experiment """

    def setup_commands(self):
        bin_path = path.join(config["llvmdir"], "bin")

        config["path"] = bin_path + ":" + config["path"]
        config["ld_library_path"] = path.join(config["llvmdir"], "lib") + \
            config["ld_library_path"]


    def __init__(self, name, projects=[]):
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

        self.populate_projects(projects)

    def populate_projects(self, projects_to_filter):
        self.projects = {}
        factories = ProjectFactory.factories
        for id in factories:
            project = factories[id].create(self)
            self.projects[project.name] = project

        if projects_to_filter:
            allkeys = Set(self.projects.keys())
            usrkeys = Set(projects_to_filter)
            self.projects = {x: self.projects[x] for x in allkeys & usrkeys}

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
        """
        Collect all project-specific results into one big result file for
        further processing. Later processing steps might have to regain
        per-project information from this file again.
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
            per_project_results = zip(*[iter(split_items)]*2)
            self.generate_report(per_project_results)

    def map_projects(self, fun, phase=None):
        for project_name in self.projects:
            prj = self.projects[project_name]
            print "============================================================"
            if phase:
                print prj.name + " (" + phase + ")"
            else:
                print prj.name
            print "============================================================"
            fun(prj)
            print "============================================================"

    def verify_product(self, filename, log = None):
        if not log:
            log = LOG

        if not path.exists(filename):
            log.error("{0} not created by project.".format(filename))


class RuntimeExperiment(Experiment):

    """ Additional runtime only features for experiments """

    def get_papi_calibration(self, p, calibrate_call):
        with local.cwd(self.builddir):
            calib_out = calibrate_call("--file", p.calibrate_prof_f,
                                       "--calls", p.calibrate_calls_f)

        rm(p.calibrate_prof_f)
        rm(p.calibrate_calls_f)

        calib_pattern = regex.compile(
            'Real time per call \(ns\): (?P<val>[0-9]+.[0-9]+)')
        for line in calib_out.split('\n'):
            res = calib_pattern.search(line)
            if res:
                return res.group('val')
        return None
