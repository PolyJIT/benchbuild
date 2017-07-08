#!/usr/bin/env python3
"""
Dump SLURM script that executes the selected experiment with all projects.

This basically provides the same as benchbuild run, except that it just
dumps a slurm batch script that executes everything as an array job
on a configurable SLURM cluster.
"""
import os
from plumbum import cli
from benchbuild.settings import CFG
from benchbuild import experiments
from benchbuild import projects
from benchbuild import experiment, project
from benchbuild.utils import slurm


class Slurm(cli.Application):
    """ Generate a SLURM script. """

    def __init__(self, executable):
        super(Slurm, self).__init__(executable)
        self._experiment = None
        self._project_names = None
        self._group_names = None
        self._description = None

    @cli.switch(["-E", "--experiment"],
                str,
                mandatory=True,
                help="Specify experiments to run")
    def experiment(self, cfg_experiment):
        """Specify experiments to run"""
        self._experiment = cfg_experiment

    @cli.switch(["-P", "--project"],
                str,
                list=True,
                requires=["--experiment"],
                help="Specify projects to run")
    def projects(self, projects):
        """Specify projects to run"""
        self._project_names = projects

    @cli.switch(["-D", "--description"],
                str,
                help="A description for this experiment run")
    def experiment_tag(self, description):
        """A description for this experiment run"""
        self._description = description

    @cli.switch(["-G", "--group"],
                str,
                list=True,
                requires=["--experiment"],
                help="Run a group of projects under the given experiments")
    def group(self, groups):
        """Run a group of projects under the given experiments"""
        self._group_names = groups

    def __go__(self, project_names, experiment):
        prj_registry = project.ProjectRegistry
        projects = prj_registry.projects
        project_names = self._project_names
        if project_names is not None:
            allkeys = set(list(projects.keys()))
            usrkeys = set(project_names)
            projects = {x: projects[x] for x in allkeys & usrkeys}

        group_names = self._group_names
        if group_names is not None:
            groupkeys = set(group_names)
            projects = {
                name: cls
                for name, cls in projects.items() if cls.GROUP in groupkeys
            }

        projects = {x: projects[x]
                    for x in projects
                    if projects[x].DOMAIN != "debug"}

        prj_keys = sorted(projects.keys())
        print("{0} Projects".format(len(prj_keys)))

        slurm.prepare_slurm_script(experiment, prj_keys)

    def main(self):
        """Main entry point of benchbuild run."""
        experiments.discover()
        projects.discover()

        exp_registry = experiment.ExperimentRegistry
        project_names = self._project_names
        exp_name = self._experiment

        if self._description:
            CFG["experiment_description"] = self._description

        CFG["slurm"]["logs"] = os.path.abspath(os.path.join(CFG[
            'build_dir'].value(), CFG['slurm']['logs'].value()))
        CFG["build_dir"] = CFG["slurm"]["node_dir"].value()

        print("Experiment: " + exp_name)
        if exp_name in exp_registry.experiments:
            exp_cls = exp_registry.experiments[exp_name]
            exp = exp_cls(project_names)

            CFG["slurm"]["node_dir"] = os.path.abspath(
                os.path.join(CFG["slurm"]["node_dir"].value(),
                             exp.id))
            self.__go__(project_names, exp)
        else:
            from logging import error
            error("Could not find {} in the experiment registry.", exp_name)
