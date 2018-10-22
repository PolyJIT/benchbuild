"""Subcommand for project handling."""
from plumbum import cli

from benchbuild import project
from benchbuild.cli.main import BenchBuild


@BenchBuild.subcommand("project")
class BBProject(cli.Application):
    """Manage BenchBuild's known projects."""

    def main(self):
        if not self.nested_command:
            self.help()


@BBProject.subcommand("view")
class BBProjectView(cli.Application):
    """View available projects."""

    groups = None

    @cli.switch(
        ["-G", "--group"],
        str,
        list=True,
        help="Include projects of this group.")
    def set_group(self, groups):
        self.groups = groups

    def main(self, *projects):
        print_projects(project.populate(projects, self.groups))


def print_projects(projects=None):
    """
    Print a list of projects registered for that experiment.

    Args:
        exp: The experiment to print all projects for.

    """
    grouped_by = {}
    if not projects:
        print(
            "Your selection didn't include any projects for this experiment.")
        return

    for name in projects:
        prj = projects[name]

        if prj.GROUP not in grouped_by:
            grouped_by[prj.GROUP] = []

        grouped_by[prj.GROUP].append("{name}/{group}".format(
            name=prj.NAME, group=prj.GROUP))

    for name in grouped_by:
        print("group: {0}".format(name))
        group_projects = sorted(grouped_by[name])
        for prj in group_projects:
            prj_cls = projects[prj]

            version_str = None
            if hasattr(prj_cls, 'versions'):
                version_str = ", ".join(prj_cls.versions())

            project_id = "{0}/{1}".format(prj_cls.NAME, prj_cls.GROUP)

            project_str = \
                "  name: {id:<32} version: {version:<24} source: {src}".format(
                    id=str(project_id),
                    version=str(prj_cls.VERSION),
                    src=str(prj_cls.SRC_FILE))
            print(project_str)
            if prj_cls.__doc__:
                docstr = prj_cls.__doc__.strip("\n ")
                print("    description: {desc}".format(desc=docstr))
            if version_str:
                print("    versions: {versions}".format(versions=version_str))
        print()
