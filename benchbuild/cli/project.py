"""Subcommand for project handling."""
import typing as tp

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
    grouped_by: tp.Dict[str, tp.List[str]] = {}
    if not projects:
        print("Your selection didn't include any projects for this experiment.")
        return

    for name in projects:
        prj = projects[name]

        if prj.GROUP not in grouped_by:
            grouped_by[prj.GROUP] = []

        grouped_by[prj.GROUP].append(
            "{name}/{group}".format(name=prj.NAME, group=prj.GROUP)
        )

    for name in grouped_by:
        print(f'::  group: {name}')
        group_projects = sorted(grouped_by[name])
        for prj_name in group_projects:
            prj_cls = projects[prj_name]

            project_id = f'{prj_cls.NAME}/{prj_cls.GROUP}'
            project_version = str(bb.source.default(*prj_cls.SOURCE))

            project_lines = [
                f'::  {project_id}'
                f'    default: {project_version:<24}'
            ]
            for src in prj_cls.SOURCE:
                source_lines = [
                    f'\n    * source: {src.local}',
                ]
                if isinstance(src.remote, str):
                    source_lines.append(f' remote: {src.remote}')
                    source_lines.extend([
                        f'\n      - {str(version)}'
                        for version in src.versions()
                    ])
                else:
                    source_lines.extend([
                        f'\n      - {str(version)} '
                        f'remote: {src.remote[str(version)]}'
                        for version in src.versions()
                    ])
                project_lines.extend(source_lines)

            print(*project_lines)
            if prj_cls.__doc__:
                docstr = prj_cls.__doc__.strip("\n ")
                print(f'    description: {docstr}')
        print()
