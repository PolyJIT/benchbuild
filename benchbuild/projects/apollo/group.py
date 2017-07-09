from os import path
from benchbuild.project import Project
from benchbuild.settings import CFG


class ApolloGroup(Project):
    GROUP = 'apollo'

    path_suffix = "src"

    def __init__(self, exp):
        super(ApolloGroup, self).__init__(exp, "apollo")
        self.sourcedir = path.join(str(CFG["src_dir"]), "src", self.name)
        self.setup_derived_filenames()
