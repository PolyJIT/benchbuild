import benchbuild.extensions as ext
import benchbuild.experiments.polyjit as pj


class Compilestats(pj.PolyJIT):
    """Gather compilestats, with enabled JIT."""

    NAME = "pj-cs"

    def actions_for_project(self, p):
        p = pj.PolyJIT.init_project(p)
        p.compiler_extension = ext.ExtractCompileStats(p, self)
        return self.default_compiletime_actions(p)
