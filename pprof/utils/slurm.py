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
from pprof import settings

INFO = logging.info
CFG = settings.CFG
CFG["slurm"] = {
    "account": {
        "desc": "The SLURM account to use by default.",
        "default": "cl"
    },
    "partition": {
        "desc": "The SLURM partition to use by default.",
        "default": "chimaira"
    },
    "script": {
        "desc":
        "Name of the script that can be passed to SLURM. Used by external tools.",
        "default": "chimaira-slurm.sh"
    },
    "cpus_per_task": {
        "desc":
        "Number of CPUs that should be requested from SLURM. Used by external tools.",
        "default": 10
    },
    "node_dir": {
        "desc":
        "Node directory, when executing on a cluster node. This is not "
        "used by pprof directly, but by external scripts.",
        "default": os.path.join(os.getcwd(), "results")
    },
    "timelimit": {
        "desc": "The timelimit we want to give to a job",
        "default": "12:00:00"
    },
    "exclusive": {
        "desc": "Shall we reserve a node exclusively, or share it with others?",
        "default": True
    },
}

def dump_slurm_script(script_name, log_name, pprof, experiment, projects,
                      **kwargs):
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
    with open(script_name, 'w') as slurm:
        slurm.write("#!/bin/sh\n")
        slurm.write("#SBATCH -o {}\n".format(log_name))
        slurm.write("#SBATCH -t \"12:00:00\"\n")
        slurm.write("#SBATCH --hint=nomultithread\n")
        slurm.write("#SBATCH --ntasks 1\n")
        slurm.write("#SBATCH --exclusive\n")
        slurm.write("#SBATCH --cpus-per-task {}\n".format(CFG["slurm"]["cpus_per_task"]))

        posargs = ['script_name', 'log_name', 'commands']
        kwargs = {k: kwargs[k] for k in kwargs if k not in posargs}
        for key in kwargs:
            slurm.write("export {env}=\"{value}\"\n".format(env=key,
                                                            value=kwargs[key]))

        slurm.write("projects=(\n")
        for project in projects:
            slurm.write("'{}'\n".format(str(project)))
        slurm.write(")\n")

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
    slurm_script = path.join(os.getcwd(), str(CFG['slurm']['script']))
    log_file = os.path.join(str(CFG['']["build_dir"]), experiment + ".log")

    # We need to wrap the pprof run inside srun to avoid HyperThreading.
    srun = local["srun"]
    srun = srun["--hint=nomultithread", pprof_c[
        "-v", "run",
        "-D", CFG['']['experiment_description'],
        "-B", CFG['slurm']["node_dir"],
        "--likwid-prefix", CFG['likwid']["prefix"], "-L", CFG['llvm']["dir"]]]
    dump_slurm_script(slurm_script,
                      log_file,
                      srun,
                      experiment,
                      projects,
                      LD_LIBRARY_PATH="{}:$LD_LIBRARY_PATH".format(
                          CFG['papi']['library']),
                      PPROF_TESTINPUTS=CFG['']["test_dir"],
                      PPROF_TMP_DIR=CFG['']["tmp_dir"],
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
        # Import t
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


def main(_projects, _groups, experiments):
    from pprof import projects  # Import all projects for the registry.
    from pprof.project import ProjectRegistry

    projects = ProjectRegistry.projects
    if _projects is not None:
        allkeys = set(list(projects.keys()))
        usrkeys = set(_projects)
        projects = {x: projects[x] for x in allkeys & usrkeys}

    if _groups is not None:
        projects = {
            name: cls
            for name, cls in projects.items() if cls.GROUP in _groups
        }

    prj_keys = sorted(projects.keys())
    for exp in experiments:
        INFO("experiment: {} with projects:".format(exp))
        INFO(", ".join(prj_keys))
        prepare_slurm_script(exp, prj_keys, uuid.uuid4())
        #dispatch_jobs(exp, prj_keys)
