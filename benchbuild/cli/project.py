"""Subcommand for project handling."""
from plumbum import cli
import benchbuild.project as project
import benchbuild.experiments.empty as empty
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



    @cli.switch(
        ["-G", "--group"],
        str,
        list=True,
        help="Include projects of this group.")
    def set_group(self, groups):
        self.groups = groups

    def main(self, *projects):
        _projects = project.populate(projects, self.groups)


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
            print("  name: {id:<32} {version:<24} {src}".format(
                id="{0}/{1}".format(prj_cls.NAME, prj_cls.GROUP),
                version="version: {0}".format(prj_cls.VERSION),
                src="source: {0}".format(prj_cls.SRC_FILE)))
            if prj_cls.__doc__:
                print("    description: {desc}".format(
                    desc=prj_cls.__doc__.strip("\n ")))
        print()
