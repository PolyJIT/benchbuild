import copy
import uuid
import benchbuild.extensions as ext
import benchbuild.experiments.polyjit as pj

from benchbuild.utils.actions import RequireAll

class PJITlikwid(pj.PolyJIT):
    """
    An experiment that uses likwid's instrumentation API for profiling.

    This instruments all projects with likwid instrumentation API calls
    in key regions of the JIT.

    This allows for arbitrary profiling of PolyJIT's overhead and run-time
    """

    NAME = "pj-likwid"

    def actions_for_project(self, p):
        from benchbuild.settings import CFG

        p = pj.PolyJIT.init_project(p)
        p.cflags = ["-DLIKWID_PERFMON"] + p.cflags

        actns = []
        for i in range(1, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(p)
            cp.run_uuid = uuid.uuid4()
            cp.runtime_extension = \
                pj.RunWithLikwid(
                    cp, self,
                    ext.RuntimeExtension(cp, self, config={'jobs': i}),
                    config={'jobs': i})

            actns.append(RequireAll(self.default_runtime_actions(cp)))
        return actns

