from os import path
from benchbuild.project import Project
from benchbuild.settings import CFG


class BenchBuildGroup(Project):
    GROUP = 'benchbuild'

    path_suffix = "src"

    def __init__(self, exp):
        super(BenchBuildGroup, self).__init__(exp, "benchbuild")
        self.sourcedir = path.join(str(CFG["src_dir"]), "src", self.name)
        self.setup_derived_filenames()
