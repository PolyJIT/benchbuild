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

    limit: int = 10

    @cli.switch(["-l", "--limit"],
                int,
                help="Limit the number of versions to display")
    def set_limit(self, limit: int) -> None:
        self.limit = limit

    def main(self, project: str) -> int:
        index = bb.populate([project], [])
        if not index.values():
            print(f'Project named {project} not found in the registry.')
            print('Maybe it is not configured to be loaded.')
            return -1
        for project_cls in index.values():
            print_project(project_cls, self.limit)
        return 0


def print_project(project: tp.Type[Project], limit: int) -> None:
    """
    Print details for a single project.

    Args:
        project: The project to print.
        limit: The maximal number of versions to print.
    """
    tmp_dir = CFG['tmp_dir']

    print(f'project: {project.NAME}')
    print(f'group: {project.GROUP}')
    print(f'domain: {project.DOMAIN}')
    print('source:')

    for source in project.SOURCE:
        if not source.is_context_free():
            continue

        num_versions = len(source.versions())

        print(' -', f'{source.remote}')
        print('  ', 'default:', source.default)
        print('  ', f'versions: {num_versions}')
        print('  ', 'local:', f'{tmp_dir}/{source.local}')
        for v in list(source.versions())[:limit]:
            print('  ' * 2, v)

    def print_layers(container: ContainerImage, indent: int = 1) -> None:
        for layer in container:
            print('  ' * indent, str(layer))

    print('container:')
    if isinstance(project.CONTAINER, ContainerImage):
        print_layers(project.CONTAINER, 1)
    else:
        for k, container in project.CONTAINER:
            print('  ', str(k))
            print_layers(container, 2)


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
        "{name_header:<{width}} | {domain_header:^15} | "
        "{source_header:^15} | {description_header}"
    )
    project_row_format = (
        "{name:<{width}} | {domain:^15} | "
        "{num_sources:^15} | {description}"
    )

    for name in grouped_by:
        group_projects = sorted(grouped_by[name])
        print(
            project_header_format.format(
                name_header=f'{name}',
                domain_header="Domain",
                source_header="# Sources",
                description_header="Description",
                width=project_column_width
            )
        )
        for prj_name in group_projects:
            prj_cls = projects[prj_name]
            project_id = f'{prj_cls.NAME}/{prj_cls.GROUP}'
            num_project_sources = len(prj_cls.SOURCE)
            docstr = ""
            if prj_cls.__doc__:
                docstr = prj_cls.__doc__.strip("\n ")
            print(
                project_row_format.format(
                    name=project_id,
                    domain=prj_cls.DOMAIN,
                    num_sources=num_project_sources,
                    description=docstr,
                    width=project_column_width
                )
            )
        print()
