import typing as tp

import rich
from plumbum import cli

from benchbuild import plugins, project, source
from benchbuild.cli.main import BenchBuild
from benchbuild.environments.domain import commands
from benchbuild.environments.service_layer import messagebus, unit_of_work
from benchbuild.project import ProjectIndex


@BenchBuild.subcommand("container")
class BenchBuildContainer(cli.Application):

    def main(self, *projects: str) -> int:
        plugins.discover()

        wanted_projects = project.populate(projects, [])
        if not wanted_projects:
            rich.print("No projects selected.")
            return -2

        create_project_containers(wanted_projects)


def enumerate_projects(
        projects: ProjectIndex) -> tp.Generator[project.Project, None, None]:
    for prj_class in projects.values():
        for variant in source.product(*prj_class.SOURCE):
            context = source.context(*variant)
            yield prj_class(context)


def create_project_containers(projects: ProjectIndex) -> None:
    for prj in enumerate_projects(projects):
        image_tag = f'{prj.name}/{prj.group}:{prj.version}'
        cmd = commands.CreateProjectImage(image_tag)
        uow = unit_of_work.BuildahUnitOfWork()
        results = messagebus.handle(cmd, uow)
        rich.print(results)
