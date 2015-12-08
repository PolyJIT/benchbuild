#!/usr/bin/env python3
# encoding: utf-8
"""
Run arbitrary pprof experiments on the Infosun Chimaira cluster.

This module prepares slurm scripts to:
    * Build
    * Run
    * Collect results
on Infosun's chimaira cluster. All the hard work is done after instancing the
pprof study on the local disks of the assigned cluster node. The results
are copied to a configurable shared directory. After all partial jobs are
completed the results are collected with a separate job.

The resource management system used on chimaira is SLURM.
"""

from plumbum import cli, local
from pprof.settings import config
import os


def dump_slurm_script(script_name, log_name, commands, **kwargs):
    """
    Dump a bash script that can be given to SLURM.

    Args:
        script_name (str): name of the bash script.
        log_name (str): name of the log file SLURM should print to.
        commands (list(plumbum.cmd)): List of plumbum commands to write
            to the bash script.
        **kwargs: Dictionary with all environment variable bindings we should
            map in the bash script.
    """
    from plumbum.cmd import chmod

    with open(script_name, 'w') as slurm:
        slurm.write("#!/bin/sh\n")
        slurm.write("#SBATCH -o {}\n".format(log_name))
        slurm.write("#SBATCH -t \"12:00:00\"\n")
        slurm.write("#SBATCH --hint=nomultithread\n")
        slurm.write("#SBATCH --ntasks 1\n")
        slurm.write("#SBATCH --exclusive\n")
        slurm.write("#SBATCH --cpus-per-task {}\n".format(config[
            "cpus-per-task"]))

        posargs = ['script_name', 'log_name', 'commands']
        kwargs = {k: kwargs[k] for k in kwargs if k not in posargs}
        for key in kwargs:
            slurm.write("export {env}=\"{value}\"\n".format(env=key,
                                                            value=kwargs[key]))
        for command in commands:
            slurm.write("{}\n".format(str(command)))
    chmod("+x", script_name)


def prepare_slurm_script(experiment, project, experiment_id):
    """
    Prepare a slurm script that executes the pprof experiment for a given project.

    :experiment: The experiment we want to execute
    :project: Filter all but the given project
    """
    from os import path

    commands = []
    if not config["llvm"]:
        config["llvm"] = path.join(config["nodedir"], "install")
    pprof_c = local["pprof"]

    slurm_script = path.join(os.getcwd(), config["slurm_script"])
    log_file = os.path.join(config["resultsdir"],
                            experiment + "-" + project + ".log")

    if config["local_build"]:
        commands.append(pprof_c["build", "-j", config[
            "cpus-per-task"], "-B", config["nodedir"], "-I", config[
                "isl"], "-L", config["likwidir"], "-P", config["papi"]])

    # We need to wrap the pprof run inside srun to avoid HyperThreading.
    srun = local["srun"]
    commands.append(srun["--hint=nomultithread", pprof_c[
        "-v", "run", "-P", project, "-E", experiment, "-D", config[
            "experiment_description"], "-B", config["nodedir"],
        "--likwid-prefix", config["likwiddir"], "-L", config["llvm"]]])
    dump_slurm_script(slurm_script,
                      log_file,
                      commands,
                      LD_LIBRARY_PATH="{}:$LD_LIBRARY_PATH".format(path.join(
                          config["papi"], "lib")),
                      PPROF_TESTINPUTS=config["testdir"],
                      PPROF_TMP_DIR=config["tmpdir"],
                      PPROF_DB_HOST=config["db_host"],
                      PPROF_DB_PORT=config["db_port"],
                      PPROF_DB_NAME=config["db_name"],
                      PPROF_DB_USER=config["db_user"],
                      PPROF_DB_PASS=config["db_pass"],
                      PPROF_EXPERIMENT_ID=experiment_id)
    return slurm_script


def prepare_directories(dirs):
    """
    Make sure that the required directories exist.

    Args:
        dirs - the directories we want.
    """
    from plumbum.cmd import mkdir

    for directory in dirs:
        mkdir("-p", directory, retcode=None)


def dispatch_jobs(exp, projects):
    """
    Dispatch sbatch scripts to slurm for all given projects.

    Args:
        projects: List of projects that need to be dispatched to SLURM

    Return:
        The list of SLURM job ids.
    """
    jobs = []
    from uuid import uuid4
    from plumbum.cmd import sbatch, awk

    experiment_id = uuid4()
    for project in projects:
        if len(project) == 0:
            continue
        slurm_script = prepare_slurm_script(exp, project, experiment_id)
        prepare_directories([config["resultsdir"]])
        sbatch_cmd = sbatch[
            "--job-name=" + exp + "-" + project, "-A", config[
                "account"], "-p", config["partition"], slurm_script]

        job_id = (sbatch_cmd | awk['{ print $4 }'])()
        jobs.append(job_id)
    return jobs


class Chimaira(cli.Application):
    """Execute the polyprof study on the chimaira cluster via slurm"""

    @cli.autoswitch(["E", "experiments"], str, list=True, mandatory=True)
    def experiments(self, exps):
        """Which experiments should be sent to SLURM."""
        config["experiments"] = exps

    @cli.autoswitch(["N", "nodedir"], str)
    def nodedir(self, dirname):
        """Where is the local directory on the cluster node."""
        config["nodedir"] = dirname

    @cli.autoswitch(["R", "resultsdir"], str)
    def resultsdir(self, dirname):
        """Where should the results be placed."""
        config["resultsdir"] = dirname

    @cli.autoswitch(int)
    def cpus_per_task(self, cpt):
        """How many CPUs we request per task."""
        config["cpus-per-task"] = cpt

    @cli.autoswitch(str)
    def likwid_prefix(self, likwid_prefix):
        """Likwid prefix."""
        config["likwiddir"] = likwid_prefix

    @cli.autoswitch(str)
    def papi_prefix(self, papi_prefix):
        """PAPI prefix."""
        config["papi"] = papi_prefix

    @cli.autoswitch(["p", "partition"], str)
    def partition(self, partition):
        """Which SLURM partition to use."""
        config["partition"] = partition

    @cli.autoswitch(["A", "account"], str)
    def account(self, account):
        """Which SLURM account to use."""
        config["account"] = account

    @cli.autoswitch(str)
    def llvm_prefix(self, llvm_prefix):
        """LLVM Prefix."""
        config["llvm"] = llvm_prefix

    @cli.autoswitch(["build"])
    def build(self):
        """Build the LLVM/Polly/Polli/Clang on the cluster node."""
        config["local_build"] = True

    @cli.autoswitch(["P", "project"], str, list=True)
    def project(self, projects):
        """Which project(s) should be sent to SLURM."""
        self._projects = projects

    @cli.autoswitch(["G", "group"], str, list=True)
    def group(self, groups):
        """Which group(s) should be sent to SLURM."""
        self._groups = groups

    @cli.autoswitch(["D", "description"], str)
    def experiment_tag(self, description):
        """A description for this experiment run."""
        config["experiment_description"] = description

    def main(self):
        from pprof import projects  # Import all projects for the registry.
        from pprof.project import ProjectRegistry

        projects = ProjectRegistry.projects
        if self._projects is not None:
            allkeys = set(list(projects.keys()))
            usrkeys = set(self._projects)
            projects = {x: projects[x] for x in allkeys & usrkeys}

        if self._groups is not None:
            projects = {
                name: cls
                for name, cls in projects.items() if cls.GROUP in self._groups
            }

        for exp in config["experiments"]:
            dispatch_jobs(exp, projects.keys())

    _projects = None
    _groups = None


if __name__ == '__main__':
    Chimaira.run()
