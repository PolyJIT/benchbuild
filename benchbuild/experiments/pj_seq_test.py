"""
The 'sequence analysis' experiment.

Generates a custom sequence for the project and  writes the compile stats
created doing so. Returns the actions executed for the test.
"""
import uuid

from functool import partial
from benchbuild.utils.actions import (MakeBuildDir, Prepare, Download,
                                    Configure, Build, Run, Clean)

from benchbuild.experiment.polyjit import PolyJIT

class Test(PolyJIT):
    """
    An experiment that excecutes all projects with PolyJIT support and analyzes
    the sequences wrote to the database.
    This shall become the default experiment for sequence analysis.
    """

    NAME = "pj-seq-test"

    def actions_for_projects(self, p):
        """Executes the actions for the test."""
        from benchbuild.settings import CFG
        # this form of import is used because of the '-' in a module-name
        generate_custom_sequence = __import__(benchbuild.experiments.\
                                          sequence-analysis.greedy.\
                                          generate_custom_sequence)


        p = PolyJIT.init_project(p)

        actions = []
        p.cflags = ["-03", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                    "-mllvm", "-polly"]
        p.run_uuid = uuid.uuid4()
        jobs = int(CFG["jobs"].value())
        p.compiler_extension = partial(generate_custom_sequence,
                                      p, self, CFG, jobs)
        actions.extend([
            MakeBuildDir(p),
            Prepare(p),
            Download(p),
            Configure(p),
            Build(p),
            Run(p),
            Clean(p)
        ])
        return actions
