"""Subcommand for project handling."""
import typing as tp
from functools import reduce

from plumbum import cli

import benchbuild as bb
from benchbuild.project import ProjectIndex


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
    project_header_format = "{:<{width}} | {:^15} | {:^15} | {}"
    project_row_format = "{:<{width}} | {:^15} | {:^15} | {}"

    for name in grouped_by:
        group_projects = sorted(grouped_by[name])
        print(
            project_header_format.format(
                f'{name}',
                "# Sources",
                "# Versions",
                "Description",
                width=project_column_width
            )
        )
        print()
        for prj_name in group_projects:
            prj_cls = projects[prj_name]
            project_id = f'{prj_cls.NAME}/{prj_cls.GROUP}'
            num_project_sources = len(prj_cls.SOURCE)
            num_combinations = reduce(
                lambda x, y: x * y,
                [len(src.versions()) for src in prj_cls.SOURCE]
            )
            docstr = ""
            if prj_cls.__doc__:
                docstr = prj_cls.__doc__.strip("\n ")
            print(
                project_row_format.format(
                    project_id,
                    num_project_sources,
                    num_combinations,
                    docstr,
                    width=project_column_width
                )
            )
        print()
