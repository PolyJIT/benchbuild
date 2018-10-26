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
from benchbuild.utils.cmd import bash, chmod
from benchbuild.utils.path import list_to_path

LOG = logging.getLogger(__name__)


def script(experiment, projects):
    """
    Prepare a slurm script that executes the experiment for a given project.

    Args:
        experiment: The experiment we want to execute
        projects: All projects we generate an array job for.
    """
    benchbuild_c = local[local.path(sys.argv[0])]
    slurm_script = local.cwd / experiment.name + "-" + str(
        CFG['slurm']['script'])

    srun = local["srun"]
    srun_args = []
    if not CFG["slurm"]["multithread"]:
        srun_args.append("--hint=nomultithread")
    if not CFG["slurm"]["turbo"]:
        srun_args.append("--pstate-turbo=off")

    srun = srun[srun_args]
    srun = srun[benchbuild_c["run"]]

    return __save__(slurm_script, srun, experiment, projects)


def __path():
    host_path = os.getenv('PATH', default='')
    env = CFG['env'].value
    benchbuild_path = list_to_path(env.get('PATH', []))
    return os.path.pathsep.join([benchbuild_path, host_path])


def __ld_library_path():
    host_path = os.getenv('LD_LIBRARY_PATH', default='')
    env = CFG['env'].value
    benchbuild_path = list_to_path(env.get('LD_LIBRARY_PATH', []))
    return os.path.pathsep.join([benchbuild_path, host_path])


def __save__(script_name, benchbuild, experiment, projects):
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
    if not __verify__(script_name):
        LOG.error("SLURM script failed verification.")
    print("SLURM script written to {0}".format(script_name))
    return script_name


def __verify__(script_name):
    """
    Verify a generated script.

    Args:
        script_name: Path to the generated script.
    """
    return (bash["-n", script_name] & TF)
