#!/usr/bin/env python
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

from plumbum import cli, local, FG
from plumbum.cmd import awk, sbatch, chmod, pprof
from pprof.settings import config
import os


def dispatch_collect_job(exp, deps):
    """
    Dispatch a collect job that waits for all jobs to finish.

    :exp:
        Which experiment do you want to collect results for
    """
    cmd = sbatch["--job-name=collect-" + exp]
    dep_string = ""
    if len(deps) > 0:
        dep_string = "--dependency=afterany"
    print deps
    for job in deps:
        dep_string = dep_string + ":" + job.rstrip()
    cmd = cmd["-A", config["account"],
              "-p", config["partition"]]
    cmd = cmd[dep_string]
    script = prepare_collect_results_script(exp)
    cmd[script] & FG


def dump_slurm_script(script_name, log_name, commands, uuid=None):
    """Write all commands into a file with the given script name and
        configure slurm to use the given log_name with it

    :script_name: Where do you want the slurm script
    :log_name: Where should we put the log output of the SLURM run
    :commands: What commands sould the script execute
    """
    from pprof.settings import config as ppcfg
    from os import path

    with open(script_name, 'w') as slurm:
        slurm.write("#!/bin/sh\n")
        slurm.write("#SBATCH -o {}\n".format(log_name))
        slurm.write("#SBATCH -t \"4:00:00\"\n")
        slurm.write("export LD_LIBRARY_PATH=\"{}:$LD_LIBRARY_PATH\"\n".format(
            path.join(config["papi"], "lib")))
        slurm.write(
            "export PPROF_TESTINPUTS=\"{}\"\n".format(ppcfg["testdir"]))
        slurm.write("export PPROF_TMP_DIR=\"{}\"\n".format(ppcfg["tmpdir"]))
        slurm.write("export PPROF_DB_HOST=\"{}\"\n".format(ppcfg["db_host"]))
        slurm.write("export PPROF_DB_PORT=\"{}\"\n".format(ppcfg["db_port"]))
        slurm.write("export PPROF_DB_NAME=\"{}\"\n".format(ppcfg["db_name"]))
        slurm.write("export PPROF_DB_USER=\"{}\"\n".format(ppcfg["db_user"]))
        slurm.write("export PPROF_DB_PASS=\"{}\"\n".format(ppcfg["db_pass"]))
        if uuid:
            slurm.write("export PPROF_EXPERIMENT_ID=\"{}\"\n".format(uuid))
        for c in commands:
            slurm.write("{}\n".format(str(c)))
    chmod("+x", script_name)


def prepare_collect_results_script(experiment):
    """Prepare a SLURM script that collects all project results

    :experiment: Which experiment we want to collect the results for
    :returns: A list of SLURM job ids

    """
    commands = []
    if not config["llvm"]:
        config["llvm"] = os.path.join(config["nodedir"], "install")
    script_name = os.path.join(os.getcwd(), config["slurm_script"])
    slurm_script = script_name + ".collect"
    log_file = os.path.join(config["resultsdir"], experiment + ".log")
    commands.append(pprof["run",
                          "-E", experiment,
                          "-B", config["resultsdir"]])
    dump_slurm_script(slurm_script, log_file, commands)
    return slurm_script


def prepare_slurm_script(experiment, project, experiment_id):
    """
    Prepare a slurm script that executes the pprof experiment for a given project.

    :experiment: The experiment we want to execute
    :project: Filter all but the given project
    """
    commands = []
    if not config["llvm"]:
        config["llvm"] = os.path.join(config["nodedir"], "install")
    pprof = local["pprof"]

    slurm_script = os.path.join(os.getcwd(), config["slurm_script"])
    log_file = os.path.join(config["resultsdir"],
                            experiment + "-" + project + ".log")

    if config["local_build"]:
        commands.append(pprof["build", "-j", config["cpus-per-task"],
                              "-B", config["nodedir"], "-I", config["isl"],
                              "-L", config["likwidir"], "-P", config["papi"]])
    commands.append(pprof["run",
                          "-P", project,
                          "-E", experiment,
                          "-B", config["nodedir"],
                          "--likwid-prefix", config["likwiddir"],
                          "-L", config["llvm"]])
    # commands.append(
    #    cp["-ar", node_results, os.path.join(config["resultsdir"],
    #                                          experiment)])
    # commands.append(mv[node_error_log, error_log])
    dump_slurm_script(slurm_script, log_file, commands, experiment_id)
    return slurm_script


def dispatch_jobs(exp, projects):
    """Dispatch sbatch scripts to slurm for all projects given

    projects: List of projects that need to be dispatched to SLURM
    :returns: a list of SLURM job ids

    """
    jobs = []
    from uuid import uuid4

    experiment_id = uuid4()
    for project in projects:
        if len(project) == 0:
            continue
        slurm_script = prepare_slurm_script(exp, project, experiment_id)
        job_id = (sbatch[
            "--job-name=" + exp + "-" + project,
            "-A", config["account"],
            "-p", config["partition"],
            "--ntasks", "1",
            "--cpus-per-task", config["cpus-per-task"],
            "--hint=nomultithread",
            slurm_script] | awk['{ print $4 }'])()
        jobs.append(job_id)
    return jobs


class Chimaira(cli.Application):

    """Execute the polyprof study on the chimaira cluster via slurm"""

    @cli.switch(["-E", "--experiment"], str, list=True, mandatory=True,
                help="Which experiments should be built")
    def experiments(self, exps):
        config["experiments"] = exps

    @cli.switch(["--nodedir"], str, help="Where to build on the node")
    def nodedir(self, dirname):
        config["nodedir"] = dirname

    @cli.switch(["--resultsdir"], str, mandatory=True,
                help="Where should the results be placed")
    def resultsdir(self, dirname):
        config["resultsdir"] = dirname

    @cli.switch(["--scriptname"], str,
                help="How should the sbatch script be called?")
    def scriptname(self, name):
        config["slurm_script"] = name

    @cli.switch(["--cpus-per-task"], int,
                help="How many cpu should we request per task?")
    def cpus_per_task(self, cpt):
        config["cpus-per-task"] = cpt

    @cli.switch(["-I"], str, help="ISL prefix")
    def isl(self, isl_prefix):
        config["isl"] = isl_prefix

    @cli.switch(["-L"], str, help="Likwid prefix")
    def likwid(self, likwid_prefix):
        config["likwiddir"] = likwid_prefix

    @cli.switch(["-P"], str, help="PAPI prefix")
    def papi(self, papi_prefix):
        config["papi"] = papi_prefix

    @cli.switch(["-p"], str, help="SLURM partition to use")
    def partition(self, partition):
        config["partition"] = partition

    @cli.switch(["-A"], str, help="SLURM account to use")
    def account(self, account):
        config["account"] = account

    @cli.switch(["--llvm-prefix"], str, help="LLVM prefix")
    def llvm(self, llvm_prefix):
        config["llvm"] = llvm_prefix

    @cli.switch(["--build"], help="Build LLVM/Polly/Polli/Clang on the node")
    def local_build(self):
        config["local_build"] = True

    def main(self):
        from itertools import chain

        # That is an awful lot of filtering required for parsing that
        # output... grmpf
        for exp in config["experiments"]:
            print "Experiment: {}".format(exp)
            pprof_list = pprof["run", "-l", "-E", exp]
            prj_list = pprof_list().split(',')
            prj_list = map(unicode.strip, prj_list)
            prj_list = map(lambda x: x.split('\n'), prj_list)
            prj_list = filter(None, prj_list)
            prj_list = list(chain.from_iterable(prj_list))
            prj_list = filter(lambda x: not '>>' in x, prj_list)
            prj_list = filter(None, prj_list)
            print "  {} projects".format(len(prj_list))
            print
            print ", ".join(prj_list)
            jobs = dispatch_jobs(exp, prj_list)
        #    dispatch_collect_job(exp, jobs)

if __name__ == '__main__':
    Chimaira.run()
