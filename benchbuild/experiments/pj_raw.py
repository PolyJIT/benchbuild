import copy
import uuid
import benchbuild.extensions as ext
import benchbuild.experiments.polyjit as pj


class PJITRaw(pj.PolyJIT):
    """
    An experiment that executes all projects with PolyJIT support.

    This is our default experiment for speedup measurements.
    """

    NAME = "pj-raw"

    def actions_for_project(self, p):
        from benchbuild.settings import CFG

        p = pj.PolyJIT.init_project(p)

        actns = []
        for i in range(2, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(p)
            cp.run_uuid = uuid.uuid4()
            cp.cflags += ["-mllvm", "-polly-num-threads={0}".format(i)]
            cp.runtime_extension = \
                ext.LogAdditionals(
                    pj.RegisterPolyJITLogs(
                        ext.RunWithTime(
                            pj.EnablePolyJIT(
                                ext.RuntimeExtension(p, self, config={
                                    "jobs": i,
                                    "cores": str(i-1),
                                    "cores-config": str(i),
                                    "recompilation": "enabled"}),
                                project=p))))

            actns.extend(self.default_runtime_actions(cp))
        return actns
