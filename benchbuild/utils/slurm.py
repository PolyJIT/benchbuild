"""
SLURM support for the benchbuild study.

This module can be used to generate bash scripts that can be executed by
the SLURM controller either as batch or interactive script.
"""
import logging
import os
import sys

from plumbum import local, TF

from benchbuild.settings import CFG
from benchbuild.utils.cmd import bash, chmod, mkdir
from benchbuild.utils.path import list_to_path

INFO = logging.info
ERROR = logging.error


def __get_slurm_path():
    host_path = os.getenv('PATH', default='')
    env = CFG['env'].value
    benchbuild_path = list_to_path(env.get('PATH', []))
    return benchbuild_path + ':' + host_path


def __get_slurm_ld_library_path():
    host_path = os.getenv('LD_LIBRARY_PATH', default='')
    env = CFG['env'].value
    benchbuild_path = list_to_path(env.get('LD_LIBRARY_PATH', []))
    return benchbuild_path + ':' + host_path


def dump_slurm_script(script_name, benchbuild, experiment, projects):
    """
    Dump a bash script that can be given to SLURM.

    Args:
        script_name (str): name of the bash script.
        commands (list(benchbuild.utils.cmd)):
            List of plumbum commands to write to the bash script.
        **kwargs: Dictionary with all environment variable bindings we should
            map in the bash script.
    """
    from jinja2 import Environment, PackageLoader

    logs_dir = os.path.dirname(CFG['slurm']['logs'].value)
    node_command = str(benchbuild["-E", experiment.name, "$_project"])
    env = Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        loader=PackageLoader('benchbuild', 'utils/templates'))
    template = env.get_template('slurm.sh.inc')

    with open(script_name, 'w') as slurm2:
        slurm2.write(
            template.render(
                config=["export " + x for x in repr(CFG).split('\n')],
                clean_lockdir=str(CFG["slurm"]["node_dir"]),
                clean_lockfile=str(CFG["slurm"]["node_dir"]) + \
                    ".clean-in-progress.lock",
                cpus=int(CFG['slurm']['cpus_per_task']),
                exclusive=bool(CFG['slurm']['exclusive']),
                lockfile=str(CFG['slurm']["node_dir"]) + ".lock",
                log=local.path(logs_dir) / str(experiment.id),
                max_running=int(CFG['slurm']['max_running']),
                name=experiment.name,
                nice=int(CFG['slurm']['nice']),
                nice_clean=int(CFG["slurm"]["nice_clean"]),
                node_command=node_command,
                no_multithreading=not CFG['slurm']['multithread'],
                ntasks=1,
                prefix=str(CFG["slurm"]["node_dir"]),
                projects=projects,
                slurm_account=str(CFG["slurm"]["account"]),
                slurm_partition=str(CFG["slurm"]["partition"]),
                timelimit=str(CFG['slurm']['timelimit']),
            )
        )

    chmod("+x", script_name)


def verify_slurm_script(script_name):
    """
    Verify a generated script.

    Args:
        script_name: Path to the generated script.
    """
    return (bash["-n", script_name] & TF)


def prepare_slurm_script(experiment, projects):
    """
    Prepare a slurm script that executes the experiment for a given project.

    Args:
        experiment: The experiment we want to execute
        projects: All projects we generate an array job for.
    """

    # Assume that we run the slurm subcommand of benchbuild.
    benchbuild_c = local[local.path(sys.argv[0])]
    slurm_script = local.cwd / experiment.name + "-" + str(
        CFG['slurm']['script'])

    # We need to wrap the benchbuild run inside srun to avoid HyperThreading.
    srun = local["srun"]
    if not CFG["slurm"]["multithread"]:
        srun = srun["--hint=nomultithread"]
    if not CFG["slurm"]["turbo"]:
        srun = srun["--pstate-turbo=off"]
    srun = srun[benchbuild_c["-v", "run"]]
    dump_slurm_script(slurm_script, srun, experiment, projects)
    if not verify_slurm_script(slurm_script):
        ERROR("SLURM script failed verification.")
    print("SLURM script written to {0}".format(slurm_script))
    return slurm_script


def prepare_directories(dirs):
    """
    Make sure that the required directories exist.

    Args:
        dirs - the directories we want.
    """

    for directory in dirs:
        mkdir("-p", directory, retcode=None)
