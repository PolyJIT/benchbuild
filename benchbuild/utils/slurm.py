"""
SLURM support for the benchbuild study.

This module can be used to generate bash scripts that can be executed by
the SLURM controller either as batch or interactive script.
"""
import logging
import os
import sys

from plumbum import local

from benchbuild.settings import CFG
from benchbuild.utils.cmd import bash, chmod, mkdir

INFO = logging.info


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
        commands (list(benchbuild.utils.cmd)):
            List of plumbum commands to write to the bash script.
        **kwargs: Dictionary with all environment variable bindings we should
            map in the bash script.
    """
    from jinja2 import Environment, PackageLoader

    logs_dir = os.path.dirname(CFG['slurm']['logs'].value())
    node_command = str(benchbuild["-P", "$_project", "-E", experiment.name])
    env = Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        loader=PackageLoader('benchbuild', 'utils/templates'))
    template = env.get_template('slurm.sh.inc')

    with open(script_name, 'w') as slurm2:
        slurm2.write(
            template.render(
                config=["export " + x for x in repr(CFG).split('\n')],
                clean_lockdir=CFG["slurm"]["node_dir"].value(),
                clean_lockfile=CFG["slurm"]["node_dir"].value() + \
                    ".clean-in-progress.lock",
                cpus=CFG['slurm']['cpus_per_task'].value(),
                exclusive=CFG['slurm']['exclusive'].value(),
                lockfile=CFG['slurm']["node_dir"].value() + ".lock",
                log=os.path.join(logs_dir, str(experiment.id)),
                max_running=CFG['slurm']['max_running'].value(),
                name=experiment.name,
                nice=CFG['slurm']['nice'].value(),
                nice_clean=CFG["slurm"]["nice_clean"].value(),
                node_command=node_command,
                no_multithreading=not CFG['slurm']['multithread'].value(),
                ntasks=1,
                prefix=CFG["slurm"]["node_dir"].value(),
                projects=projects,
                slurm_account=CFG["slurm"]["account"].value(),
                slurm_partition=CFG["slurm"]["partition"].value(),
                timelimit=CFG['slurm']['timelimit'].value(),
            )
        )

    bash("-n", script_name)
    chmod("+x", script_name)


def prepare_slurm_script(experiment, projects):
    """
    Prepare a slurm script that executes the experiment for a given project.

    Args:
        experiment: The experiment we want to execute
        projects: All projects we generate an array job for.
    """

    # Assume that we run the slurm subcommand of benchbuild.
    benchbuild_c = local[os.path.abspath(sys.argv[0])]
    slurm_script = os.path.join(
        os.getcwd(), experiment.name + "-" + str(CFG['slurm']['script']))

    # We need to wrap the benchbuild run inside srun to avoid HyperThreading.
    srun = local["srun"]
    if not CFG["slurm"]["multithread"].value():
        srun = srun["--hint=nomultithread"]
    if not CFG["slurm"]["turbo"].value():
        srun = srun["--pstate-turbo=off"]
    srun = srun[benchbuild_c["-v", "run"]]
    dump_slurm_script(slurm_script, srun, experiment, projects)
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
