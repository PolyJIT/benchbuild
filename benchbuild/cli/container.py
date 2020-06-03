"""Subcommand for containerizing benchbuild experiments."""
import copy
from typing import Dict, List

import attr
import rich
import rx
from plumbum import cli
from rich import traceback
from rich.progress import BarColumn, Progress, TaskID
from rx import operators as ops

from benchbuild import environments as envs
from benchbuild import experiment, plugins, project, streams
from benchbuild.cli.main import BenchBuild
from benchbuild.typing import ExperimentT, ProjectT


@BenchBuild.subcommand("container")
class BenchBuildContainer(cli.Application):
    experiment_args: List[str] = []
    group_args: List[str] = []

    @cli.switch(["-E", "--experiment"],
                str,
                list=True,
                help="Specify experiments to run")
    def set_experiments(self, names: List[str]) -> None:
        self.experiment_args = names

    @cli.switch(["-G", "--group"],
                str,
                list=True,
                requires=["--experiment"],
                help="Run a group of projects under the given experiments")
    def set_group(self, groups: List[str]) -> None:
        self.group_args = groups

    force = cli.Flag(["-f", "--force"])

    def main(self, *projects: str) -> int:
        """Main entry point of benchbuild container."""
        view = BuildView()
        plugins.discover()
        cli_experiments = self.experiment_args
        cli_groups = self.group_args

        # 1. Select Projects/Experiments
        discovered_experiments = experiment.discovered()
        wanted_experiments = dict(
            filter(lambda pair: pair[0] in set(cli_experiments),
                   discovered_experiments.items()))
        unknown_experiments = list(
            filter(lambda name: name not in discovered_experiments.keys(),
                   set(cli_experiments)))

        if unknown_experiments:
            rich.print('Could not find ', str(unknown_experiments),
                       ' in the experiment registry.')
        if not wanted_experiments:
            rich.print("Could not find any experiment. Exiting.")
            return -2

        wanted_projects = project.populate(projects, cli_groups)
        if not wanted_projects:
            rich.print("No projects selected.")
            return -2

        project_stream = construct_project_images(wanted_projects, self.force)
        experiment_stream = construct_experiment_images(wanted_projects,
                                                        wanted_experiments,
                                                        self.force)

        # Count tasks per group and prepare the view
        task_counts = rx.concat(project_stream, experiment_stream).pipe(
            ops.flat_map(lambda group: group.pipe(
                ops.count(), ops.map(lambda cnt: (group.key, cnt)))))
        task_counts.subscribe(
            lambda event: view.view_task(event[0], event[1], ''))

        # Run all tasks per group and update the view
        task_runs = rx.concat(project_stream, experiment_stream).pipe(
            ops.flat_map(lambda group: group.pipe(
                ops.starmap(lambda prj, task:
                            (group.key, task(prj.container))))))

        def on_error(o: Exception) -> None:
            view.print_exception()

        def on_next(o) -> None:
            return view.update(o[0], f'✓ {o[1]}')

        task_runs.subscribe(on_next, on_error)

        # FIXME: Error handling.
        return 0


@attr.s
class BuildView:
    progress: Progress = attr.ib(init=False)
    tasks: Dict[str, TaskID] = attr.ib(init=False)

    def __attrs_post_init__(self):
        traceback.install()
        self.progress = Progress("[progress.description]{task.description}",
                                 BarColumn(),
                                 "[progress.percentage]{task.remaining}",
                                 "{task.fields[message]}")
        self.tasks = dict()

    def view_task(self, name: str, count: str, message: str):
        if name not in self.tasks:
            self.tasks[name] = self.progress.add_task(name,
                                                      total=count,
                                                      message=message)

    def update(self, name: str, message: str):
        if name in self.tasks:
            self.progress.update(self.tasks[name],
                                 advance=1,
                                 refresh=True,
                                 message=message)

    def print_exception(self) -> None:
        self.progress.console.print_exception()

    def print(self, *args, **kwargs):
        self.progress.print(*args, **kwargs)

    def done(self):
        self.progress.stop()


def construct_project_images(cli_projects: Dict[str, ProjectT],
                             force: bool = False) -> rx.Observable:
    """
    Constructs all project images requested by the user.

    This will invoke a set of container image builds with caching.

    Args:
        cli_projects: A dictionary of all selected (name,project_class)
                         tuples taken from the project registry.
        force: Enforces image construction (disables caching).

    Returns:
        An observable stream of image build jobs
    """

    # Augment the user-defined project image declarations.
    return streams.project_stream(cli_projects.values()).pipe(
        # Build a stream of project containers
        envs.is_cached(force),
        ops.map(envs.add_benchbuild),
        ops.map(envs.add_project_sources),
        envs.commit(envs.mktag),
        # Build a grouped task stream
        ops.map(envs.materialize),
        ops.merge_all(),
        ops.group_by(key_mapper=lambda o: f'{o[0].name}',
                     subject_mapper=rx.subject.ReplaySubject))


def construct_experiment_images(cli_projects: Dict[str, ProjectT],
                                cli_experiments: Dict[str, ExperimentT],
                                force: bool = False) -> rx.Observable:
    """
    Constructs all experiment images requested by the user.

    This will invoke a container image build for each built project container.
    This also assumes that the required project containers have been built
    before.

    Args:
        cli_projects: A dictionary of all selected (`name`,`ProjectT`)
                         tuples taken from the project registry.
        cli_experiments: A dictionary of all selected (`name`,`ExperimentT`)
                         tuples taken from the project registry.
        force: Enforces image construction (disables caching).
    Returns:
        An observable stream of container build jobs
    """
    experiment_stream = streams.experiment_stream(cli_experiments.values())
    return streams.project_stream(cli_projects.values()).pipe(
        ops.flat_map(lambda prj: experiment_stream.pipe(
            envs.add_experiment(prj), envs.commit(envs.mktag, prj))),
        ops.map(envs.materialize), ops.merge_all(),
        ops.group_by(key_mapper=lambda o: f'{o[0].name}',
                     subject_mapper=rx.subject.ReplaySubject))
