"""Subcommand for containerizing benchbuild experiments."""
import sys
from typing import (Any, Callable, Dict, Generator, List, Optional, Tuple,
                    Type, Union)

import attr
import rx
from plumbum import cli
from rich import print
from rich.progress import BarColumn, Progress, TaskID
from rx import operators as ops

from benchbuild import environments as envs
from benchbuild import experiment, plugins, project, streams
from benchbuild.cli.main import BenchBuild
from benchbuild.source.variants import VariantContext
from benchbuild.typing import CommandFunc, ExperimentT, ProjectT


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

        main2(wanted_projects, wanted_experiments)

        return 0


def main2(wanted_projects: Dict[str, ProjectT],
          wanted_experiments: Dict[str, ExperimentT]):
    view = BuildView()

    #experiment_stream = rx.from_iterable(wanted_experiments.values())

    def filter_cached(combined: Tuple[ProjectT, VariantContext]) -> bool:
        prj, var = combined
        return not envs.is_cached(prj, var)

    project_images = streams.from_projects(wanted_projects.values()).pipe(
        ops.filter(filter_cached),
        ops.do_action(on_next=view.print),
        ops.starmap(lambda p, v: {
            'project': p,
            'variant': v
        }),
    )

    def build_image(elem: Dict[str, Any]) -> None:
        prj = elem['project']
        var = elem['variant']
        img = prj.CONTAINER

        envs.add_benchbuild(img)
        envs.add_project_sources(var, img)
        envs.commit(prj, var)

    # Augment the user-defined project image declarations.
    project_images.subscribe(on_next=build_image)

    # Build a grouped task stream
    project_tasks = project_images.pipe(
        ops.map(lambda o: (o['project'], o['variant'])),
        ops.starmap(envs.materialize), ops.merge_all(),
        ops.group_by(key_mapper=lambda o: o[0].NAME,
                     subject_mapper=lambda: rx.subject.ReplaySubject()))

    # Count tasks per group and prepare the view
    task_counts = project_tasks.pipe(
        ops.flat_map(lambda group: group.pipe(
            ops.do_action(on_next=view.print), ops.count(),
            ops.map(lambda cnt: (group.key, cnt)))))
    task_counts.subscribe(lambda event: view.view_task(event[0], event[1], ''))

    # Run the tasks per group and update the view
    def run_task(name: str, task: CommandFunc) -> None:
        message = task()
        return (name, message)

    task_runs = project_tasks.pipe(
        ops.flat_map(lambda group: group.pipe(
            ops.starmap(lambda prj, var, task:
                        (group.key, task)), ops.starmap(run_task))))
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
