import typing as tp
from functools import partial

from plumbum import cli, local

from benchbuild import experiment, plugins, project, settings, source
from benchbuild.environments.domain import commands, declarative
from benchbuild.environments.service_layer import messagebus, unit_of_work
from benchbuild.experiment import ExperimentIndex
from benchbuild.project import ProjectIndex
from benchbuild.settings import CFG


class BenchBuildContainer(cli.Application):  # type: ignore
    experiment_args: tp.List[str] = []
    group_args: tp.List[str] = []

    @cli.switch(["-E", "--experiment"],
                str,
                list=True,
                help="Specify experiments to run")  # type: ignore
    def set_experiments(self, names: tp.List[str]) -> None:  # type: ignore
        self.experiment_args = names

    @cli.switch(["-G", "--group"],
                str,
                list=True,
                requires=["--experiment"],
                help="Run a group of projects under the given experiments"
               )  # type: ignore
    def set_group(self, groups: tp.List[str]) -> None:  # type: ignore
        self.group_args = groups

    def main(self, *projects: str) -> int:
        plugins.discover()

        cli_experiments = self.experiment_args
        cli_groups = self.group_args

        discovered_experiments = experiment.discovered()
        wanted_experiments = {
            name: cls
            for name, cls in discovered_experiments.items()
            if name in set(cli_experiments)
        }
        unknown_experiments = [
            name for name in cli_experiments
            if name not in set(discovered_experiments.keys())
        ]

        if unknown_experiments:
            print(
                'Could not find ', str(unknown_experiments),
                ' in the experiment registry.'
            )
        if not wanted_experiments:
            print("Could not find any experiment. Exiting.")
            return -2

        wanted_projects = project.populate(list(projects), cli_groups)
        if not wanted_projects:
            print("No projects selected.")
            return -2

        create_base_images(wanted_experiments, wanted_projects)
        create_project_images(wanted_experiments, wanted_projects)
        create_experiment_images(wanted_experiments, wanted_projects)
        run_experiment_images(wanted_experiments, wanted_projects)

        return 0


def enumerate_projects(
    experiments: ExperimentIndex, projects: ProjectIndex
) -> tp.Generator[project.Project, None, None]:
    for exp_class in experiments.values():
        for prj_class in projects.values():
            for context in exp_class.sample(prj_class):
                prj = prj_class(context)
                if prj.container:
                    yield prj


def make_version_tag(*versions: source.Variant) -> str:
    return '-'.join([str(v) for v in versions])


def make_image_name(name: str, tag: str) -> str:
    return f'{name}:{tag}'


def create_base_images(
    experiments: ExperimentIndex, projects: ProjectIndex
) -> None:
    """
    Create base images requested by all selected projects.

    The images will contain benchbuild and requirer all dependencies to be
    installed during construction. BenchBuild will insert itself at the end
    of the layer sequence.

    Args:
        projects: A project index that contains all reqquested (name, project)
                  Tuples.
    """
    image_commands: tp.Set[commands.Command] = set()

    for prj in enumerate_projects(experiments, projects):
        image = prj.container
        if not image.base in declarative.DEFAULT_BASES:
            continue

        layers = declarative.DEFAULT_BASES[image.base]
        declarative.add_benchbuild_layers(layers)

        cmd: commands.Command = commands.CreateBenchbuildBase(
            image.base, layers
        )
        image_commands.add(cmd)

    for cmd in image_commands:
        uow = unit_of_work.ContainerImagesUOW()
        messagebus.handle(cmd, uow)


def __pull_sources_in_context(prj: project.Project) -> None:
    for version in prj.variant.values():
        src = version.owner
        src.version(local.cwd, str(version))


BB_APP_ROOT: str = '/app'


def create_project_images(
    experiments: ExperimentIndex, projects: ProjectIndex
) -> None:
    """
    Create project images for all selected projects.

    The image will contain all sources the project requires.

    Args:
        projects: A project index that contains all reqquested (name, project)
                  Tuples.
    """
    build_dir = local.path(BB_APP_ROOT) / 'results'

    for prj in enumerate_projects(experiments, projects):
        version = make_version_tag(*prj.variant.values())
        image_tag = make_image_name(f'{prj.name}/{prj.group}', version)

        layers = prj.container
        layers.context(partial(__pull_sources_in_context, prj))
        layers.add('.', BB_APP_ROOT)
        layers.run('mkdir', str(build_dir))
        layers.env(
            BB_BUILD_DIR=str(build_dir),
            BB_TMP_DIR=BB_APP_ROOT,
            BB_PLUGINS_PROJECTS=f'["{prj.__module__}"]'
        )
        layers.workingdir(BB_APP_ROOT)

        cmd = commands.CreateImage(image_tag, layers)
        uow = unit_of_work.ContainerImagesUOW()
        messagebus.handle(cmd, uow)


def enumerate_experiments(
    experiments: ExperimentIndex, projects: ProjectIndex
) -> tp.Generator[experiment.Experiment, None, None]:
    for exp_class in experiments.values():
        prjs = list(enumerate_projects(experiments, projects))
        yield exp_class(projects=prjs)


def create_experiment_images(
    experiments: ExperimentIndex, projects: ProjectIndex
) -> None:
    """
    Create experiment images for all selected experiments.

    This spawns new container images for each project assigned to the
    experiment. The project image becomes the new base for the experiment
    image.

    The image will be prepared to run only the given experiment/project
    combination by default.

    Args:
        experiments: An experiment index that contains all requested
                     (name, experiment) Tuples.
        projects: A project index that contains all reqquested (name, project)
                  Tuples.
    """
    for exp in enumerate_experiments(experiments, projects):
        for prj in exp.projects:
            version = make_version_tag(*prj.variant.values())
            base_tag = make_image_name(f'{prj.name}/{prj.group}', version)
            image_tag = make_image_name(
                f'{exp.name}/{prj.name}/{prj.group}', version
            )

            image = declarative.ContainerImage().from_(base_tag)
            image.extend(exp.container)
            image.env(BB_PLUGINS_EXPERIMENTS=f'["{exp.__module__}"]')
            verbosity = int(settings.CFG['verbosity'])
            image.env(BB_VERBOSITY=f'{verbosity}')

            image.entrypoint('benchbuild', 'run', '-E', exp.name, str(prj.id))

            cmd = commands.CreateImage(image_tag, image)
            uow = unit_of_work.ContainerImagesUOW()

            messagebus.handle(cmd, uow)


def run_experiment_images(
    experiments: ExperimentIndex, projects: ProjectIndex
) -> None:
    """
    Run experiments on given projects.

    This expects all images to be existent in the repository.

    Args:
        experiments: Index of experiments to run.
        projects: Index of projects to run.
    """

    build_dir = str(CFG['build_dir'])
    uow = unit_of_work.ContainerImagesUOW()

    for exp in enumerate_experiments(experiments, projects):
        for prj in exp.projects:
            version = make_version_tag(*prj.variant.values())
            image_tag = make_image_name(
                f'{exp.name}/{prj.name}/{prj.group}', version
            )

            container_name = f'{exp.name}_{prj.name}_{prj.group}'

            cmd = commands.RunProjectContainer(
                image_tag, container_name, build_dir
            )

            messagebus.handle(cmd, uow)
