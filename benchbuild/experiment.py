"""
BenchBuild's skeleton for experiments.

An benchbuild.experiment defines a series of phases that constitute a
benchbuild compatible experiment. This is the default implementation of an
experiment.

Clients can derive from class class::benchbuild.experiment.Experiment and
override the methods relvant to their experiment.

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
from abc import abstractmethod
import uuid
import typing as t

import regex
from plumbum import local

import benchbuild.projects as all_projects
import benchbuild.project as prj
import benchbuild.settings as settings
from benchbuild.project import Project
from benchbuild.project import ProjectRegistry
from benchbuild.settings import CFG
from benchbuild.utils.actions import (Build, Clean, CleanExtra, Configure,
                                      Download, MakeBuildDir, Prepare,
                                      Run, RequireAll)


def get_group_projects(group: str, experiment) -> t.List[Project]:
    """
    Get a list of project names for the given group.

    Filter the projects assigned to this experiment by group.

    Args:
        group (str): The group.
        experiment (benchbuild.Experiment): The experiment we draw our projects
            to filter from.

    Returns (list):
        A list of project names for the group that are supported by this
        experiment.
    """
    group = []
    projects = experiment.projects
    for name in projects:
        project = projects[name]

        if project.group_name == group:
            group.append(name)
    return group


class ExperimentRegistry(type):
    """Registry for benchbuild experiments."""

    experiments = {}

    def __init__(cls, name, bases, dict):
        """Register a project in the registry."""
        super(ExperimentRegistry, cls).__init__(name, bases, dict)

        if cls.NAME is not None:
            ExperimentRegistry.experiments[cls.NAME] = cls


class Experiment(object, metaclass=ExperimentRegistry):
    """
    A series of commands executed on a project that form an experiment.

    The default implementation should provide a sane environment for all
    derivates.

    One important task executed by the basic implementation is setting up
    the default set of projects that belong to this project.
    As every project gets registered in the ProjectFactory, the experiment
    gets a list of experiment names that work as a filter.

    """

    NAME = None

    def __new__(cls, *args, **kwargs):
        """Create a new experiment instance and set some defaults."""
        new_self = super(Experiment, cls).__new__(cls)
        if cls.NAME is None:
            raise AttributeError(
                "{0} @ {1} does not define a NAME class attribute.".format(
                    cls.__name__, cls.__module__))
        new_self.name = cls.NAME
        return new_self

    def __init__(self, projects=None, group=None):
        self.projects = {}
        self.sourcedir = CFG["src_dir"].value()
        self.builddir = str(CFG["build_dir"].value())
        self.testdir = CFG["test_dir"].value()
        self._actions = []

        cfg_exps = CFG["experiments"].value()
        if self.name in cfg_exps:
            self.id = cfg_exps[self.name]
        else:
            self.id = str(uuid.uuid4())
            cfg_exps[self.name] = self.id
            CFG["experiments"] = cfg_exps
        self.populate_projects(projects, group)

    def populate_projects(self, projects_to_filter=None, group=None):
        """
        Populate the list of projects that belong to this experiment.

        Args:
            projects_to_filter (list):
                List of projects we want to assign to this experiment.
                We intersect the list of projects with the list of supported
                projects to get the list of projects that belong to this
                experiment.
            group (str):
                In addition to the project filter, we provide a way to filter
                whole groups.
        """
        self.projects = {}
        all_projects.discover()
        prjs = ProjectRegistry.projects
        if projects_to_filter:
            allkeys = set(list(prjs.keys()))
            usrkeys = set(projects_to_filter)
            prjs = {x: prjs[x] for x in allkeys & usrkeys}

        if group:
            prjs = {
                name: cls
                for name, cls in prjs.items() if cls.GROUP == group
            }

        if projects_to_filter is None:
            projects_to_filter = []

        self.projects = {
            x: prjs[x] for x in prjs
            if prjs[x].DOMAIN != "debug" or x in projects_to_filter}

    @abstractmethod
    def actions_for_project(self, project):
        """
        Get the actions a project wants to run.

        Args:
            project (benchbuild.Project): the project we want to run.
        """

    def actions(self):
        actions = []

        for project in self.projects:
            p = self.projects[project](self)
            actions.append(Clean(p))
            actions.append(RequireAll(self.actions_for_project(p)))

        actions.append(CleanExtra(self))
        return actions

    @staticmethod
    def default_runtime_actions(project):
        """Return a series of actions for a run time experiment."""
        return [
            MakeBuildDir(project),
            Prepare(project),
            Download(project),
            Configure(project),
            Build(project),
            Run(project),
            Clean(project)
        ]

    @staticmethod
    def default_compiletime_actions(project):
        """Return a series of actions for a compile time experiment."""
        return [
            MakeBuildDir(project),
            Prepare(project),
            Download(project),
            Configure(project),
            Build(project),
            Clean(project)
        ]


class RuntimeExperiment(Experiment):
    """Additional runtime only features for experiments."""

    def get_papi_calibration(self, project, calibrate_call):
        """
        Get calibration values for PAPI based measurements.

        Args:
            project (Project):
                Unused (deprecated).
            calibrate_call (benchbuild.utils.cmd):
                The calibration command we will use.
        """
        with local.cwd(self.builddir):
            with local.env(BB_USE_DATABASE=0, BB_USE_CSV=0, BB_USE_FILE=0):
                calib_out = calibrate_call()

        calib_pattern = regex.compile(
            r'Real time per call \(ns\): (?P<val>[0-9]+.[0-9]+)')
        for line in calib_out.split('\n'):
            res = calib_pattern.search(line)
            if res:
                return res.group('val')
        return None

    def persist_calibration(self, project, cmd, calibration):
        """
        Persist the result of a calibration call.

        Args:
            project (benchbuild.Project):
                The calibration values will be assigned to this project.
            cmd (benchbuild.utils.cmd):
                The command we used to generate the calibration values.
            calibration (int):
                The calibration time in nanoseconds.
        """
        if calibration:
            from benchbuild.utils.db import create_run
            from benchbuild.utils import schema as s

            run, session = create_run(
                str(cmd), project.name, self.name, project.run_uuid)
            metric = s.Metric(name="papi.calibration.time_ns",
                              value=calibration,
                              run_id=run.id)
            session.add(metric)
            session.commit()
