#!/usr/bin/env python3
"""
Dump SLURM script that executes the selected experiment with all projects.

This basically provides the same as pprof run, except that it just
dumps a slurm batch script that executes everything as an array job
on a configurable SLURM cluster.
"""
import os
import uuid
import pprint
from plumbum import cli
from pprof.settings import CFG
from pprof.experiments import *
from pprof import experiment, project, projects
from pprof.utils import slurm


class Slurm(cli.Application):
    """ Generate a SLURM script. """

    def __init__(self, executable):
        super(Slurm, self).__init__(executable)
        self._experiment = None
        self._project_names = None
        self._group_name = None

    @cli.switch(["-E", "--experiment"],
                str,
                mandatory=True,
                help="Specify experiments to run")
    def experiment(self, experiment):
        self._experiment = experiment

    @cli.switch(["-P", "--project"],
                str,
                list=True,
                requires=["--experiment"],
                help="Specify projects to run")
    def projects(self, projects):
        self._project_names = projects

    @cli.switch(["-D", "--description"],
                str,
                help="A description for this experiment run")
    def experiment_tag(self, description):
        CFG["experiment_description"] = description

    @cli.switch(["-G", "--group"],
                str,
                requires=["--experiment"],
                help="Run a group of projects under the given experiments")
    def group(self, group):
        self._group_name = group

    def __go__(self, project_names, group_name, exp_name):
        prj_registry = project.ProjectRegistry
        projects = prj_registry.projects
        project_names = self._project_names
        group_name = self._group_name
        if project_names is not None:
            allkeys = set(list(projects.keys()))
            usrkeys = set(project_names)
            projects = {x: projects[x] for x in allkeys & usrkeys}

        if group_name is not None:
            projects = {
                name: cls
                for name, cls in projects.items() if cls.GROUP == group_name
            }

        prj_keys = sorted(projects.keys())
        print("Projects:")
        pprint.pprint(prj_keys)

        slurm.prepare_slurm_script(exp_name, prj_keys, uuid.uuid4())

    def main(self):
        """Main entry point of pprof run."""
        exp_registry = experiment.ExperimentRegistry
        project_names = self._project_names
        group_name = self._group_name
        exp_name = self._experiment

        print("Experiment: " + exp_name)
        if exp_name in exp_registry.experiments:
            self.__go__(project_names, group_name, exp_name)
        else:
            from logging import error
            error("Could not find {} in the experiment registry.", exp_name)
