"""
SLURM support for the benchbuild study.

This module can be used to generate bash scripts that can be executed by
the SLURM controller either as batch or interactive script.
"""
import logging
import os
import sys
import typing as tp
from functools import reduce
from pathlib import Path

import jinja2
from plumbum import local
from plumbum.commands.base import BoundCommand

from benchbuild.experiment import Experiment
from benchbuild.settings import CFG
from benchbuild.utils import cmd
from benchbuild.utils.cmd import bash, chmod
from benchbuild.utils.path import list_to_path
from benchbuild.utils.requirements import (
    Requirement,
    get_slurm_options_from_config,
    merge_slurm_options,
)

LOG = logging.getLogger(__name__)


def script(experiment: 'Experiment', *subcommands: str) -> str:
    """
    Prepare a slurm script that executes the experiment for a given project.

    Args:
        experiment: The experiment we want to execute
        *subcommands: The subcommands to call on each SLURM node.
    """
    projects = __expand_project_versions__(experiment)
    benchbuild_c = local[local.path(sys.argv[0])]
    slurm_script = local.cwd / experiment.name + "-" + str(
        CFG['slurm']['script']
    )

    srun = cmd["srun"]
    srun_args = []
    if not CFG["slurm"]["multithread"]:
        srun_args.append("--hint=nomultithread")
    if not CFG["slurm"]["turbo"]:
        srun_args.append("--pstate-turbo=off")

    srun = srun[srun_args]
    srun = srun[benchbuild_c[subcommands]]

    return __save__(slurm_script, srun, experiment, projects)


def __expand_project_versions__(experiment: Experiment) -> tp.Iterable[str]:
    project_types = experiment.projects
    expanded = []

    for project_type in project_types:
        for revision in experiment.sample(project_type):
            project = project_type(revision=revision)
            expanded.append(project.id)
    return expanded


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


def __save__(
    script_name: str, benchbuild: BoundCommand, experiment: 'Experiment',
    projects: tp.Iterable[str]
) -> str:
    """
    Dump a bash script that can be given to SLURM.

    Args:
        script_name (str): name of the bash script.
        commands (list(benchbuild.utils.cmd)):
            List of plumbum commands to write to the bash script.
        **kwargs: Dictionary with all environment variable bindings we should
            map in the bash script.
    Raises:
        jinja2.exceptions.TemplateNotFound:
            If the modified template location does not exist.
    """
    logs_dir = Path(str(CFG['slurm']['logs'].value))
    if logs_dir.suffix != '':
        logs_dir = logs_dir.parent / logs_dir.stem
        LOG.warning(
            'Config slurm:logs should be a folder, defaulting to %s.', logs_dir
        )

    if not logs_dir.exists():
        logs_dir.mkdir()

    node_command = str(benchbuild["-E", experiment.name, "$_project"])
    template_name = str(CFG["slurm"]["template"])

    if local.path(template_name).exists():
        template_path = local.path(template_name).dirname
        template_name = local.path(template_name).basename
        loader = jinja2.FileSystemLoader(template_path)
    else:
        loader = jinja2.PackageLoader('benchbuild', 'res')

    env = jinja2.Environment(
        trim_blocks=True, lstrip_blocks=True, loader=loader
    )
    template = env.get_template(template_name)
    if len(experiment.projects) > 1:
        project_options = reduce(
            lambda x, y: merge_slurm_options(x, y.REQUIREMENTS),
            experiment.projects, tp.cast(tp.List[Requirement], [])
        )
    elif len(experiment.projects) == 1:
        project_options = experiment.projects[0].REQUIREMENTS
    else:
        project_options = []

    slurm_options = merge_slurm_options(
        project_options, experiment.REQUIREMENTS
    )
    slurm_options = merge_slurm_options(
        slurm_options, get_slurm_options_from_config()
    )

    prefix = local.path(str(CFG['slurm']['node_dir']), str(experiment.id))

    with open(script_name, 'w') as slurm2:
        slurm2.write(
            template.render(
                config=["export " + x for x in repr(CFG).split('\n')],
                clean_lockdir=str(prefix),
                clean_lockfile=prefix.with_suffix('.clean-in-progress.lock'),
                cpus=int(CFG['slurm']['cpus_per_task']),
                lockfile=prefix.with_suffix('.lock'),
                log=logs_dir.resolve() / str(experiment.id),
                max_running=int(CFG['slurm']['max_running']),
                name=experiment.name,
                nice_clean=int(CFG["slurm"]["nice_clean"]),
                node_command=node_command,
                ntasks=1,
                prefix=prefix,
                projects=projects,
                slurm_account=str(CFG["slurm"]["account"]),
                slurm_partition=str(CFG["slurm"]["partition"]),
                sbatch_options='\n'.join([
                    s_opt.to_option() for s_opt in slurm_options
                ]),
            )
        )

    chmod("+x", script_name)
    if not __verify__(script_name):
        LOG.error("SLURM script failed verification.")
    print("SLURM script written to {0}".format(script_name))
    return script_name


def __verify__(script_name: str) -> tp.Any:
    """
    Verify a generated script.

    Args:
        script_name: Path to the generated script.
    """
    return bash["-n", script_name].run_tf()
