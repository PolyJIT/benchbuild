"""
SLURM support for the benchbuild study.

This module can be used to generate bash scripts that can be executed by
the SLURM controller either as batch or interactive script.
"""
import logging
import os
from plumbum import local
from benchbuild.utils.cmd import bash, chmod, mkdir  # pylint: disable=E0401
from benchbuild.utils.path import template_str
from benchbuild.settings import CFG

INFO = logging.info


def __prepare_node_commands(experiment):
    """Get a list of bash commands that prepare the SLURM node."""
    exp_id = CFG["experiment_id"].value()
    prefix = CFG["slurm"]["node_dir"].value()
    node_image = CFG["slurm"]["node_image"].value()
    llvm_src = CFG["llvm"]["dir"].value().rstrip("/")
    llvm_tgt = os.path.join(prefix, experiment).rstrip("/")
    lockfile = prefix + ".lock"

    CFG["llvm"]["dir"] = llvm_tgt
    lines = template_str("templates/slurm-prepare-node.inc.sh")
    lines = lines.format(prefix=prefix,
                         llvm_src=llvm_src,
                         llvm_tgt=llvm_tgt,
                         lockfile=lockfile,
                         node_image=node_image)

    return lines


def __cleanup_node_commands(logfile):
    exp_id = CFG["experiment_id"].value()
    prefix = CFG["slurm"]["node_dir"].value()
    lockfile = os.path.join(prefix + ".clean-in-progress.lock")
    slurm_account = CFG["slurm"]["account"]
    slurm_partition = CFG["slurm"]["partition"]
    lines = template_str("templates/slurm-cleanup-node.inc.sh")
    lines = lines.format(lockfile=lockfile,
                         lockdir=prefix,
                         prefix=prefix,
                         slurm_account=slurm_account,
                         slurm_partition=slurm_partition,
                         logfile=logfile,
                         nice_clean=CFG["slurm"]["nice_clean"].value())
    return lines


def __get_slurm_path():
    host_path = os.getenv('PATH', default='')
    benchbuild_path = CFG['path'].value()
    return benchbuild_path + ':' + host_path


def __get_slurm_ld_library_path():
    host_path = os.getenv('LD_LIBRARY_PATH', default='')
    benchbuild_path = CFG['ld_library_path'].value()
    return benchbuild_path + ':' + host_path

def dump_slurm_script(script_name, benchbuild, experiment, projects):
    """
    Dump a bash script that can be given to SLURM.

    Args:
        script_name (str): name of the bash script.
        commands (list(benchbuild.utils.cmd)): List of plumbum commands to write
            to the bash script.
        **kwargs: Dictionary with all environment variable bindings we should
            map in the bash script.
    """
    log_path = os.path.join(CFG['slurm']['logs'].value())
    slurm_path = __get_slurm_path()
    slurm_ld = __get_slurm_ld_library_path()
    max_running_jobs = CFG['slurm']['max_running'].value()
    with open(script_name, 'w') as slurm:
        lines = """#!/bin/bash
#SBATCH -o /dev/null
#SBATCH -t \"{timelimit}\"
#SBATCH --ntasks 1
#SBATCH --cpus-per-task {cpus}
"""

        slurm.write(lines.format(log=str(log_path),
                                 timelimit=str(CFG['slurm']['timelimit']),
                                 cpus=str(CFG['slurm']['cpus_per_task'])))

        if not CFG['slurm']['multithread'].value():
            slurm.write("#SBATCH --hint=nomultithread\n")
        if CFG['slurm']['exclusive'].value():
            slurm.write("#SBATCH --exclusive\n")
        slurm.write("#SBATCH --array=0-{0}".format(len(projects) - 1))
        slurm.write("%{0}\n".format(max_running_jobs) if max_running_jobs > 0
                    else '\n')
        slurm.write("#SBATCH --nice={0}\n".format(CFG["slurm"]["nice"].value()))

        slurm.write("projects=(\n")
        for project in projects:
            slurm.write("'{0}'\n".format(str(project)))
        slurm.write(")\n")
        slurm.write("_project=\"${projects[$SLURM_ARRAY_TASK_ID]}\"\n")
        slurm_log_path = os.path.join(
            os.path.dirname(CFG['slurm']['logs'].value()), '$_project')
        slurm.write("exec 1> {log}\n".format(log=slurm_log_path))
        slurm.write("exec 2>&1\n")

        slurm.write(__prepare_node_commands(experiment))
        slurm.write("\n")
        cfg_vars = repr(CFG).split('\n')
        cfg_vars = "\nexport ".join(cfg_vars)
        slurm.write("export ")
        slurm.write(cfg_vars)
        slurm.write("\n")
        slurm.write("export PATH={p}\n".format(p=slurm_path))
        slurm.write("export LD_LIBRARY_PATH={p}\n".format(p=slurm_ld))
        slurm.write("\n")
        slurm.write("scontrol update JobId=$SLURM_JOB_ID ")
        slurm.write("JobName=\"{0} $_project\"\n".format(experiment))
        slurm.write("\n")

        # Write the experiment command.
        slurm.write(__cleanup_node_commands(slurm_log_path))
        slurm.write(str(benchbuild["-P", "$_project", "-E", experiment]) + "\n")

    bash("-n", script_name)
    chmod("+x", script_name)


def prepare_slurm_script(experiment, projects):
    """
    Prepare a slurm script that executes the benchbuild experiment for a given project.

    Args:
        experiment: The experiment we want to execute
        projects: All projects we generate an array job for.
    """
    from os import path

    benchbuild_c = local["benchbuild"]
    slurm_script = path.join(os.getcwd(),
                             experiment + "-" + str(CFG['slurm']['script']))

    # We need to wrap the benchbuild run inside srun to avoid HyperThreading.
    srun = local["srun"]
    if not CFG["slurm"]["multithread"].value():
        srun = srun["--hint=nomultithread"]
    srun = srun[benchbuild_c["-v", "run"]]
    print("SLURM script written to {0}".format(slurm_script))
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
