from functools import partial

import benchbuild.experiments.polyjit as pj


class PJITRegression(pj.PolyJIT):
    """
    This experiment will generate a series of regression tests.

    This can be used every time a new revision is produced for PolyJIT, as
    it will automatically collect any new SCoPs detected, using the JIT.

    The collection of the tests itself is intgrated into the JIT, so this
    experiment looks a lot like a RAW experiment, except we don't run
    anything.
    """

    NAME = "pj-collect"

    def actions_for_project(self, project):
        from benchbuild.settings import CFG
        from benchbuild.utils.run import track_execution

        def _track_compilestats(project, experiment, config, clang,
                                **kwargs):
            """Compile the project and track the compilestats."""
            from benchbuild.settings import CFG

            CFG.update(config)
            clang = clang["-mllvm", "-polli-collect-modules"]
            with track_execution(clang, project, experiment) as run:
                run()

        project = pj.PolyJIT.init_project(project)
        project.cflags = ["-DLIKWID_PERFMON"] + project.cflags
        project.compiler_extension = partial(_track_compilestats,
                                             project, self, CFG)
        return self.default_compiletime_actions(project)
