from pprof.project import Project
from pprof.settings import CFG
from os import path


class PprofGroup(Project):
    GROUP = 'pprof'

    path_suffix = "src"

    def __init__(self, exp):
        super(PprofGroup, self).__init__(exp, "pprof")
        self.sourcedir = path.join(str(CFG["sourcedir"]), "src", self.name)
        self.setup_derived_filenames()
