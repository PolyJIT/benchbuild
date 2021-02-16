"""Subcommand for project handling."""
import typing as tp
from functools import reduce

from plumbum import cli

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.project import ProjectIndex, Project
from benchbuild.settings import CFG


class BBProject(cli.Application):
    """Manage BenchBuild's known projects."""

    def main(self):
        if not self.nested_command:
            self.help()


@BBProject.subcommand("view")
class BBProjectView(cli.Application):
    """View available projects."""

    groups = None

    @cli.switch(["-G", "--group"],
                str,
                list=True,
                help="Include projects of this group.")
    def set_group(self, groups):
        self.groups = groups

    def main(self, *projects: str) -> int:
        print_projects(bb.populate(list(projects), self.groups))
        return 0


@BBProject.subcommand("details")
class BBProjectDetails(cli.Application):
    """Show details for a project."""

    def main(self, project: str) -> int:
        index = bb.populate([project], [])
        if not index.values():
            print(f'Project named {project} not found in the registry.')
            print('Maybe it is not configured to be loaded.')
            return -1
        for project_cls in index.values():
            print_project(project_cls)
        return 0


def print_project(project: tp.Type[Project]) -> None:
    tmp_dir = CFG['tmp_dir']

    print(f'project: {project.NAME}')
    print(f'group: {project.GROUP}')
    print(f'domain: {project.DOMAIN}')
    print('source:')
    for source in project.SOURCE:
        num_versions = len(source.versions())

        print(' -', f'{source.remote}')
        print('  ', 'default:', source.default)
        print('  ', f'versions: {num_versions}')
        print('  ', 'local:', f'{tmp_dir}/{source.local}')
        for v in list(source.versions()):
            print('  ' * 2, v)
    containers = []
    if isinstance(project.CONTAINER, ContainerImage):
        containers.append(project.CONTAINER)
    else:
        containers.extend(containers)

    print('container:')
    for container in containers:
        print(' ', container)


def print_projects(projects: ProjectIndex) -> None:
    """
    Print the information about available projects.

    Args:
        projects: The populated project index to print.

    """
    if not projects:
        print("Your selection didn't include any projects for this experiment.")
        return

    grouped_by: tp.Dict[str, tp.List[str]] = {}
    for prj in set(projects.values()):
        if prj.GROUP not in grouped_by:
            grouped_by[prj.GROUP] = []

        grouped_by[prj.GROUP].append(
            "{name}/{group}".format(name=prj.NAME, group=prj.GROUP)
        )

    project_column_width = max([
        len(f'{p.NAME}/{p.GROUP}') for p in projects.values()
    ])
    project_header_format = (
        "{name_header:<{width}} | {source_header:^15} | "
        "{version_header:^15} | {description_header}"
    )
    project_row_format = (
        "{name:<{width}} | {num_sources:^15} | "
        "{num_combinations:^15} | {description}"
    )

    for name in grouped_by:
        group_projects = sorted(grouped_by[name])
        print(
            project_header_format.format(
                name_header=f'{name}',
                source_header="# Sources",
                version_header="# Versions",
                description_header="Description",
                width=project_column_width
            )
        )
        for prj_name in group_projects:
            prj_cls = projects[prj_name]
            project_id = f'{prj_cls.NAME}/{prj_cls.GROUP}'
            num_project_sources = len(prj_cls.SOURCE)
            num_combinations = reduce(
                lambda x, y: x * y,
                [len(list(src.versions())) for src in prj_cls.SOURCE]
            )
            docstr = ""
            if prj_cls.__doc__:
                docstr = prj_cls.__doc__.strip("\n ")
            print(
                project_row_format.format(
                    name=project_id,
                    num_sources=num_project_sources,
                    num_combinations=num_combinations,
                    description=docstr,
                    width=project_column_width
                )
            )
        print()
