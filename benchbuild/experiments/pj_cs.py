import benchbuild.extensions as ext
import benchbuild.experiments.compilestats as cs
import benchbuild.experiments.polyjit as pj


class Compilestats(pj.PolyJIT):
    """Gather compilestats, with enabled JIT."""

    NAME = "pj-cs"
    SCHEMA = [cs.CompileStat.__table__]

    def actions_for_project(self, project):
        project = pj.PolyJIT.init_project(project)
        project.compiler_extension = \
            ext.RunWithTimeout(ext.ExtractCompileStats(project, self))
        return self.default_compiletime_actions(project)
