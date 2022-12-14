import typing as tp
from functools import partial

import rich
from plumbum import cli, local
from rich import print

from benchbuild import experiment, plugins, project, settings, source
from benchbuild.environments import bootstrap
from benchbuild.environments.domain import commands, declarative
from benchbuild.experiment import ExperimentIndex
from benchbuild.project import ProjectIndex
from benchbuild.settings import CFG

rich.traceback.install()


class BenchBuildContainer(cli.Application):
    """
    Top-level command for benchbuild containers.
    """

    def main(self, *args: str) -> int:
        del args

        if not self.nested_command:
            self.help()

        return 0


@BenchBuildContainer.subcommand("run")
class BenchBuildContainerRun(cli.Application):
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

    image_export = cli.Flag(['export'],
                            default=False,
                            help="Export container images to EXPORT_DIR")

    image_import = cli.Flag(['import'],
                            default=False,
                            help="Import container images from EXPORT_DIR")

    replace = cli.Flag(['replace'],
                       default=False,
                       requires=['experiment'],
                       help='Replace existing container images.')

    debug = cli.Flag(['debug'],
                     default=False,
                     requires=['experiment'],
                     help='Debug failed image builds interactively.')

    interactive = cli.Flag(['interactive'],
                           default=False,
                           requires=['experiment', 'debug'],
                           help='Run a container interactively.')

    def main(self, *projects: str) -> int:
        plugins.discover()

        if self.replace:
            CFG['container']['replace'] = self.replace

        if self.debug:
            CFG['container']['keep'] = self.debug

        if self.interactive:
            CFG['container']['interactive'] = self.interactive

        cli_experiments = self.experiment_args
        cli_groups = self.group_args

        wanted_experiments, wanted_projects = cli_process(
            cli_experiments, projects, cli_groups
        )

        if not wanted_experiments:
            print("Could not find any experiment. Exiting.")
            return -2

        if not wanted_projects:
            print("No projects selected.")
            return -2

        tasks = {
            "Base images":
                partial(
                    create_base_images, wanted_experiments, wanted_projects,
                    self.image_export, self.image_import
                ),
            "Project images":
                partial(
                    create_project_images, wanted_experiments, wanted_projects
                ),
            "Experiment images":
                partial(
                    create_experiment_images, wanted_experiments,
                    wanted_projects
                ),
            "Run":
                partial(
                    run_experiment_images, wanted_experiments, wanted_projects
                )
        }

        console = rich.get_console()

        def run_tasks() -> None:
            for name, task in tasks.items():
                print(f'Working on: {name}')
                task()

        if not self.debug:
            with console.status("[bold green]Preparing container run."):
                run_tasks()
        else:
            run_tasks()

        return 0


@BenchBuildContainer.subcommand("bases")
class BenchBuildContainerBase(cli.Application):
    """
    Prepare all base images for the selected projects and experiments.
    """
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

    image_export = cli.Flag(['export'],
                            default=False,
                            help="Export container images to EXPORT_DIR")
    image_import = cli.Flag(['import'],
                            default=False,
                            help="Import container images from EXPORT_DIR")
    debug = cli.Flag(['debug'],
                     default=False,
                     requires=['experiment'],
                     help='Debug failed image builds interactively.')

    def main(self, *projects: str) -> int:
        plugins.discover()

        if self.debug:
            CFG['container']['keep'] = self.debug

        cli_experiments = self.experiment_args
        cli_groups = self.group_args

        wanted_experiments, wanted_projects = cli_process(
            cli_experiments, projects, cli_groups
        )

        if not wanted_experiments:
            print("Could not find any experiment. Exiting.")
            return -2

        if not wanted_projects:
            print("No projects selected.")
            return -2

        tasks = {
            "Base images":
                partial(
                    create_base_images, wanted_experiments, wanted_projects,
                    self.image_export, self.image_import
                ),
        }

        console = rich.get_console()

        def run_tasks() -> None:
            for name, task in tasks.items():
                print(f'Working on: {name}')
                task()

        if not self.debug:
            with console.status("[bold green]Preparing container base images."):
                run_tasks()
        else:
            run_tasks()

        return 0


@BenchBuildContainer.subcommand("rmi")
class BenchBuildContainerRemoveImages(cli.Application):
    """
    Prepare all base images for the selected projects and experiments.
    """
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

    delete_project_images = cli.Flag(['with-projects'],
                                     default=False,
                                     help="Delete project images too")

    def main(self, *projects: str) -> int:
        plugins.discover()

        cli_experiments = self.experiment_args
        cli_groups = self.group_args

        wanted_experiments, wanted_projects = cli_process(
            cli_experiments, projects, cli_groups
        )

        if not wanted_experiments:
            print("Could not find any experiment. Exiting.")
            return -1

        if not wanted_projects:
            print("No projects selected.")
            return -1

        tasks = {
            "Remove selected images":
                partial(
                    remove_images, wanted_experiments, wanted_projects,
                    self.delete_project_images
                )
        }

        console = rich.get_console()

        def run_tasks() -> None:
            for name, task in tasks.items():
                print(f'Working on: {name}')
                task()

        with console.status("[bold green]Deleting images."):
            run_tasks()

        return 0


def cli_process(
    cli_experiments: tp.Iterable[str], cli_projects: tp.Iterable[str],
    cli_groups: tp.Iterable[str]
) -> tp.Tuple[ExperimentIndex, ProjectIndex]:
    """
    Shared CLI processing of projects/experiment selection.
    """
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

    wanted_projects = project.populate(list(cli_projects), list(cli_groups))

    return (wanted_experiments, wanted_projects)


def enumerate_projects(
    experiments: ExperimentIndex, projects: ProjectIndex
) -> tp.Generator[project.Project, None, None]:
    for exp_class in experiments.values():
        for prj_class in projects.values():
            for context in exp_class.sample(prj_class):
                prj = prj_class(context)
                if prj.container:
                    yield prj
                else:
                    version = make_version_tag(prj.revision)
                    image_tag = make_image_name(
                        f'{prj.name}/{prj.group}', version
                    )

                    rich.get_console().print(
                        f"Skipping empty container image declaration for: {image_tag}"
                    )


def make_version_tag(revision: source.Revision) -> str:
    return '-'.join([str(v) for v in revision.variants])


def make_image_name(name: str, tag: str) -> str:
    return commands.oci_compliant_name(f'{name}:{tag}')


def export_image(image_name: str) -> None:
    """
    Export the image layers to the filesystem.
    """
    publish = bootstrap.bus()
    export_name = commands.fs_compliant_name(image_name)
    export_path = local.path(
        CFG["container"]["export"].value
    ) / export_name + ".tar"
    publish(commands.ExportImage(image_name, str(export_path)))


def import_image(image_name: str) -> None:
    """
    Import the image layers to the registry.
    """
    publish = bootstrap.bus()
    import_name = commands.fs_compliant_name(image_name)
    import_path = local.path(
        CFG["container"]["import"].value
    ) / import_name + ".tar"
    publish(commands.ImportImage(image_name, str(import_path)))


def create_base_images(
    experiments: ExperimentIndex, projects: ProjectIndex, do_export: bool,
    do_import: bool
) -> None:
    """
    Create base images requested by all selected projects.

    The images will contain benchbuild and require all dependencies to be
    installed during construction. BenchBuild will insert itself at the end
    of the layer sequence.

    Args:
        projects: A project index that contains all reqquested (name, project)
                  Tuples.
    """
    publish = bootstrap.bus()
    image_commands: tp.Set[commands.CreateBenchbuildBase] = set()

    for prj in enumerate_projects(experiments, projects):
        image = prj.container

        if do_import:
            import_image(image.base)

        if not image.base in declarative.DEFAULT_BASES:
            continue

        layers = declarative.DEFAULT_BASES[image.base]
        declarative.add_benchbuild_layers(layers)

        image_commands.add(commands.CreateBenchbuildBase(image.base, layers))

    for cmd in image_commands:
        publish(cmd)

        if do_export:
            export_image(cmd.name)


def __pull_sources_in_context(prj: project.Project) -> None:
    for version in prj.revision.variants:
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
    publish = bootstrap.bus()

    for prj in enumerate_projects(experiments, projects):
        version = make_version_tag(prj.revision)
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
        publish(cmd)


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
    publish = bootstrap.bus()
    for exp in enumerate_experiments(experiments, projects):
        for prj in exp.projects:
            version = make_version_tag(prj.revision)
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

            publish(commands.CreateImage(image_tag, image))


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
    publish = bootstrap.bus()

    for exp in enumerate_experiments(experiments, projects):
        for prj in exp.projects:
            version = make_version_tag(prj.revision)
            image_tag = make_image_name(
                f'{exp.name}/{prj.name}/{prj.group}', version
            )

            container_name = f'{exp.name}_{prj.name}_{prj.group}'

            publish(
                commands.RunProjectContainer(
                    image_tag, container_name, build_dir
                )
            )


def remove_images(
    experiments: ExperimentIndex, projects: ProjectIndex,
    delete_project_images: bool
) -> None:
    """
    Remove all selected images from benchbuild's image registry.
    """
    publish = bootstrap.bus()

    for exp in enumerate_experiments(experiments, projects):
        for prj in exp.projects:
            version = make_version_tag(prj.revision)
            image_tag = make_image_name(
                f'{exp.name}/{prj.name}/{prj.group}', version
            )
            publish(commands.DeleteImage(image_tag))

    if delete_project_images:
        for prj in enumerate_projects(experiments, projects):
            version = make_version_tag(prj.revision)
            image_tag = make_image_name(f'{prj.name}/{prj.group}', version)

            publish(commands.DeleteImage(image_tag))
