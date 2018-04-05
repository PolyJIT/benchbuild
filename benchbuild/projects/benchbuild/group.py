from benchbuild.project import Project


class BenchBuildGroup(Project):
    GROUP = 'benchbuild'

    path_suffix = "src"

    def __init__(self, exp):
        super(BenchBuildGroup, self).__init__(exp, "benchbuild")
