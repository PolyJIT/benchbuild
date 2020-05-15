"""Subcommand for containerizing benchbuild experiments."""
import copy
import sys
from typing import Dict, List

import attr
import rx
from plumbum import cli
from rich import print
from rich.progress import BarColumn, Progress, TaskID
from rx import operators as ops

from benchbuild import environments as envs
from benchbuild import experiment, plugins, project, streams
from benchbuild.cli.main import BenchBuild
from benchbuild.typing import ProjectT


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
            print('Could not find ', str(unknown_experiments),
                  ' in the experiment registry.')
        if not wanted_experiments:
            print("Could not find any experiment. Exiting.")
            return -2

        wanted_projects = project.populate(projects, cli_groups)
        if not wanted_projects:
            print("No projects selected.")
            return -2

        view = BuildView()
        construct_project_images(wanted_projects, view, self.force)

        return 0


@attr.s
class BuildView:
    progress: Progress = attr.ib(init=False)
    tasks: Dict[str, TaskID] = attr.ib(init=False)

    def __attrs_post_init__(self):
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

    def print(self, *args, **kwargs):
        self.progress.print(*args, **kwargs)

    def done(self):
        self.progress.stop()


def construct_project_images(cli_projects: Dict[str, ProjectT],
                             view: BuildView,
                             force: bool = False) -> None:
    """
    Constructs all project images requested by the user.

    This will invoke a set of container image builds with caching.

    Args:
        cli_projects: A dictionary of all selected (name,project_class)
                         tuples taken from the project registry.
        view: The BuildView we print our progress to.
        force: Enforces image construction (disables caching).
    """

    # Augment the user-defined project image declarations.
    project_stream = streams.project_stream(cli_projects.values()).pipe(
        ops.map(copy.deepcopy),
        # Build a stream of project containers
        envs.is_cached(force),
        ops.map(envs.add_benchbuild),
        ops.map(envs.add_project_sources),
        ops.map(envs.commit),
        # Build a grouped task stream
        ops.map(envs.materialize),
        ops.merge_all(),
        ops.group_by(key_mapper=lambda o: o[0].name,
                     subject_mapper=rx.subject.ReplaySubject))

    # Count tasks per group and prepare the view
    task_counts = project_stream.pipe(
        ops.flat_map(lambda group: group.pipe(
            ops.count(), ops.map(lambda cnt: (group.key, cnt)))))
    task_counts.subscribe(lambda event: view.view_task(event[0], event[1], ''))

    # Run all tasks per group and update the view
    task_runs = project_stream.pipe(
        ops.flat_map(lambda group: group.pipe(
            ops.starmap(lambda prj, task: (group.key, task(prj.container))))))
    task_runs.subscribe(on_next=lambda res: view.update(res[0], res[1]),
                        on_error=view.print)

    # FIXME: Error handling.

    sys.exit(0)


#def experiment_builder(image_infos: List[Dict[str, str]],
#                       exp: ExperimentT) -> rx.Observable:
#    def on_subscribe(
#            observer: rx.typing.Observer,
#            _: Optional[rx.typing.Scheduler] = None) -> rx.typing.Disposable:
#
#        task_name = f'{exp.NAME}'
#        observer.on_next(BuildNewTask(task_name, len(image_infos)))
#        for image in image_infos:
#            from_ = image['id']
#            repo = image['repo']
#            version = image['version']
#            tag = f'{exp.NAME}/{repo}:{version}'
#
#            res = build_experiment_image(tag, from_, exp)
#            observer.on_next(BuildResult(task_name, None, res))
#        observer.on_completed()
#
#    return rx.create(on_subscribe)

#def build_experiment_image(tag: str, from_: str, exp: ExperimentT) -> str:
#
#    def cache_lookup(imageid: str) -> bool:
#        image_info = environments.by_id(imageid)
#        if "FromImageID" in image_info:
#            return image_info["FromImageID"]
#        return None
#
#    cache = cache_lookup(tag)
#    if cache:
#        return cache
#
#    container = envs.Buildah()
#    container.from_(from_)
#    return container.finalize(tag)
