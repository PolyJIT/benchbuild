import typing as tp
from functools import partial

from plumbum import cli, local

from benchbuild import experiment, plugins, project, source
from benchbuild.cli.main import BenchBuild
from benchbuild.environments.domain import commands, declarative
from benchbuild.environments.service_layer import messagebus, unit_of_work
from benchbuild.experiment import ExperimentIndex
from benchbuild.project import ProjectIndex


@BenchBuild.subcommand("container")
class BenchBuildContainer(cli.Application):
    experiment_args: tp.List[str] = []
    group_args: tp.List[str] = []

    @cli.switch(["-E", "--experiment"],
                str,
                list=True,
                help="Specify experiments to run")
    def set_experiments(self, names: tp.List[str]) -> None:
        self.experiment_args = names

    @cli.switch(["-G", "--group"],
                str,
                list=True,
                requires=["--experiment"],
                help="Run a group of projects under the given experiments")
    def set_group(self, groups: tp.List[str]) -> None:
        self.group_args = groups

    def main(self, *projects: str) -> int:
        plugins.discover()

        cli_experiments = self.experiment_args
        cli_groups = self.group_args

        discovered_experiments = experiment.discovered()
        wanted_experiments = dict(
            filter(lambda pair: pair[0] in set(cli_experiments),
                   discovered_experiments.items()))
        unknown_experiments = list(
            filter(lambda name: name not in discovered_experiments.keys(),
                   set(cli_experiments)))

        if unknown_experiments:
            print('Could not find ', str(unknown_experiments),
                  ' in the experiment registry.')
        if not wanted_experiments:
            print("Could not find any experiment. Exiting.")
            return -2

        wanted_projects = project.populate(projects, cli_groups)
        if not wanted_projects:
            print("No projects selected.")
            return -2

        create_base_images(wanted_projects)
        create_project_images(wanted_projects)
        create_experiment_images(wanted_experiments, wanted_projects)


def enumerate_projects(
        projects: ProjectIndex) -> tp.Generator[project.Project, None, None]:
    for prj_class in projects.values():
        for variant in source.product(*prj_class.SOURCE):
            context = source.context(*variant)
            yield prj_class(context)


def make_version_tag(*versions) -> str:
    return '-'.join([str(v) for v in versions])


def make_image_name(name: str, tag: str) -> str:
    return f'{name}:{tag}'


def create_base_images(projects: ProjectIndex) -> None:
    print("The following base images are available:")
    image_commands: tp.Set[commands.Command] = set()

    for prj in enumerate_projects(projects):
        image = prj.container
        if not image.base in declarative.DEFAULT_BASES:
            continue

        layers = declarative.DEFAULT_BASES[image.base]
        declarative.add_benchbuild_layers(layers)

        cmd = commands.CreateBenchbuildBase(image.base, layers)
        image_commands.add(cmd)

    for cmd in image_commands:
        uow = unit_of_work.BuildahUnitOfWork()
        results = messagebus.handle(cmd, uow)

        for res in results:
            print('  ', res)


def __pull_sources_in_context(prj: project.Project) -> None:
    for version in prj.variant.values():
        src = version.owner
        src.version(local.cwd, str(version))


def create_project_images(projects: ProjectIndex) -> None:
    print("The following images are available:")
    for prj in enumerate_projects(projects):
        version = make_version_tag(*prj.variant.values())
        image_tag = make_image_name(f'{prj.name}/{prj.group}', version)

        layers = prj.container
        layers.context(partial(__pull_sources_in_context, prj))
        layers.add('.', '/app')
        layers.env(BB_BUILD_DIR='/app',
                   BB_TMP_DIR='/app',
                   BB_PLUGINS_PROJECTS=f'["{prj.__module__}"]')
        layers.workingdir('/app')

        cmd = commands.CreateImage(image_tag, layers)
        uow = unit_of_work.BuildahUnitOfWork()
        results = messagebus.handle(cmd, uow)

        for res in results:
            print('  ', res)


def enumerate_experiments(
        experiments: ExperimentIndex, projects: ProjectIndex
) -> tp.Generator[experiment.Experiment, None, None]:
    for exp_class in experiments.values():
        prjs = list(enumerate_projects(projects))
        yield exp_class(projects=prjs)


def create_experiment_images(experiments: ExperimentIndex,
                             projects: ProjectIndex) -> None:
    print("The following images are available:")
    for exp in enumerate_experiments(experiments, projects):
        for prj in exp.projects:
            version = make_version_tag(*prj.variant.values())
            base_tag = make_image_name(f'{prj.name}/{prj.group}', version)
            image_tag = make_image_name(f'{exp.name}/{prj.name}/{prj.group}',
                                        version)

            image = declarative.ContainerImage().from_(base_tag)
            image.extend(exp.container)
            image.env(BB_PLUGINS_EXPERIMENTS=f'["{exp.__module__}"]')

            cmd = commands.CreateImage(image_tag, image)
            uow = unit_of_work.BuildahUnitOfWork()

            results = messagebus.handle(cmd, uow)

            for res in results:
                print('  ', res)
