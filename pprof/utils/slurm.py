"""
SLURM support for the pprof study.

This module can be used to generate bash scripts that can be executed by
the SLURM controller either as batch or interactive script.
"""
import logging
import os
from plumbum import local
from plumbum.cmd import chmod, mkdir # pylint: disable=E0401
from pprof.settings import CFG

INFO = logging.info


def dump_slurm_script(script_name, pprof, experiment, projects):
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
        lines = """#!/bin/sh
#SBATCH -o {log}
#SBATCH -t \"{timelimit}\"
#SBATCH --ntasks 1
#SBATCH --cpus-per-task {cpus}
"""

        slurm.write(lines.format(log=str(CFG['slurm']['logs']),
                                 timelimit=str(CFG['slurm']['timelimit']),
                                 cpus=str(CFG['slurm']['cpus_per_task'])))

        if not CFG['slurm']['multithread'].value():
            slurm.write("#SBATCH --hint=nomultithread\n")
        if CFG['slurm']['exclusive'].value():
            slurm.write("#SBATCH --exclusive\n")
        slurm.write("#SBATCH --array=0-{}\n".format(len(projects) - 1))

        slurm.write("projects=(\n")
        for project in projects:
            slurm.write("'{}'\n".format(str(project)))
        slurm.write(")\n")
        cfg_vars = repr(CFG).split('\n')
        cfg_vars = "\nexport ".join(cfg_vars)
        slurm.write("export ")
        slurm.write(cfg_vars)
        slurm.write("\n")
        slurm.write(str(pprof["-P", "${projects[$SLURM_ARRAY_TASK_ID]}", "-E",
                              experiment]))
    chmod("+x", script_name)


def prepare_slurm_script(experiment, projects):
    """
    Prepare a slurm script that executes the pprof experiment for a given project.

    Args:
        experiment: The experiment we want to execute
        projects: All projects we generate an array job for.
    """
    from os import path

    pprof_c = local["pprof"]
    slurm_script = path.join(os.getcwd(),
                             experiment + "-" + str(CFG['slurm']['script']))

    # We need to wrap the pprof run inside srun to avoid HyperThreading.
    srun = local["srun"]
    if not CFG["slurm"]["multithread"].value():
        srun = srun["--hint=nomultithread"]
    srun = srun[pprof_c["-v", "run", ]]
    print("SLURM script written to {}".format(slurm_script))
    dump_slurm_script(slurm_script, srun, experiment, projects)
    return slurm_script


def prepare_directories(dirs):
    """
    Make sure that the required directories exist.

    Args:
        dirs - the directories we want.
    """

    for directory in dirs:
        mkdir("-p", directory, retcode=None)
