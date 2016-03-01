"""
SLURM support for the pprof study.

This module can be used to generate bash scripts that can be executed by
the SLURM controller either as batch or interactive script.
"""
import logging
import os
import uuid
from plumbum import local
from plumbum.cmd import chmod, mkdir, awk # pylint: disable=E0401
from pprof.settings import CFG

INFO = logging.info
def dump_slurm_script(script_name, pprof, experiment, projects,
                      **kwargs):
    """
    Dump a bash script that can be given to SLURM.

    Args:
        script_name (str): name of the bash script.
        commands (list(plumbum.cmd)): List of plumbum commands to write
            to the bash script.
        **kwargs: Dictionary with all environment variable bindings we should
            map in the bash script.
    """
    with open(script_name, 'w') as slurm:
        lines = """
#!/bin/sh
#SBATCH -o {log}
#SBATCH -t \"{timelimit}\"
#SBATCH --ntasks 1
#SBATCH --cpus-per-task {cpus}
"""
        slurm.write(lines.format(log=str(CFG['slurm']['logs']),
                                 timelimit=str(CFG['slurm']['timelimit']),
                                 cpus=str(CFG['slurm']['cpus_per_task'])))

        if not CFG['slurm']['multithread'].value():
            slurm.write("#SBATCH --hint=nomultithreadn")
        if CFG['slurm']['exclusive'].value():
            slurm.write("#SBATCH --exclusive\n")
        slurm.write("#SBATCH --array=0-{}\n".format(len(projects)-1))

        slurm.write("projects=(\n")
        for project in projects:
            slurm.write("'{}'\n".format(str(project)))
        slurm.write(")\n")
        cfg_vars = repr(CFG).split('\n')
        cfg_vars = "\nexport ".join(cfg_vars)
        slurm.write("export ")
        slurm.write(cfg_vars)
        slurm.write(str(pprof["-P", "${projects[$SLURM_ARRAY_TASK_ID]}",
                              "-E", experiment]))
    chmod("+x", script_name)


def prepare_slurm_script(experiment, projects, experiment_id):
    """
    Prepare a slurm script that executes the pprof experiment for a given project.

    :experiment: The experiment we want to execute
    :project: Filter all but the given project
    """
    from os import path

    pprof_c = local["pprof"]
    slurm_script = path.join(os.getcwd(),
                             experiment + "-" + str(CFG['slurm']['script']))

    # We need to wrap the pprof run inside srun to avoid HyperThreading.
    srun = local["srun"]
    srun = srun["--hint=nomultithread", pprof_c[
        "-v", "run",
        "-D", CFG['experiment_description'],
        "-B", CFG['slurm']["node_dir"],
        "--likwid-prefix", CFG['likwid']["prefix"], "-L", CFG['llvm']["dir"]]]
    print("SLURM script written to {}".format(slurm_script))
    dump_slurm_script(slurm_script,
                      srun,
                      experiment,
                      projects,
                      LD_LIBRARY_PATH="{}:$LD_LIBRARY_PATH".format(
                          CFG['papi']['library']),
                      PPROF_TESTINPUTS=CFG["test_dir"],
                      PPROF_TMP_DIR=CFG["tmp_dir"],
                      PPROF_DB_HOST=CFG['db']["host"],
                      PPROF_DB_PORT=CFG['db']["port"],
                      PPROF_DB_NAME=CFG['db']["name"],
                      PPROF_DB_USER=CFG['db']["user"],
                      PPROF_DB_PASS=CFG['db']["pass"],
                      PPROF_EXPERIMENT_ID=experiment_id)
    return slurm_script


def prepare_directories(dirs):
    """
    Make sure that the required directories exist.

    Args:
        dirs - the directories we want.
    """

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
    # Import sbatch as late, because we don't want pprof to fail, if the
    # user does not have sbatch, before he actually wants to use the slurm
    # support.
    from plumbum.cmd import sbatch  # pylint: disable=E0401
    jobs = []

    experiment_id = uuid.uuid4()
    for project in projects:
        if len(project) == 0:
            continue
        slurm_script = prepare_slurm_script(exp, project, experiment_id)
        prepare_directories([CFG[""]["resultsdir"]])
        sbatch_cmd = sbatch[
            "--job-name=" + exp + "-" + project, "-A", CFG[
                "account"], "-p", CFG["partition"], slurm_script]

        job_id = (sbatch_cmd | awk['{ print $4 }'])()
        jobs.append(job_id)
    return jobs
