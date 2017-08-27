import copy
import functools as ft
import os
import uuid

import benchbuild.experiments.polyjit as pj

from plumbum import local


def run_with_perf(project, experiment, config, jobs, run_f, args, **kwargs):
    """
    Run the given binary wrapped with time.

    Args:
        project: The benchbuild.project.
        experiment: The benchbuild.experiment.
        config: The benchbuild.settings.config.
        jobs: Number of cores we should use for this exection.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::benchbuild.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
    """
    from benchbuild.settings import CFG
    from benchbuild.utils.run import track_execution
    from benchbuild.utils.db import persist_perf, persist_config
    from benchbuild.utils.cmd import perf

    CFG.update(config)
    project.name = kwargs.get("project_name", project.name)
    run_cmd = local[run_f]
    run_cmd = run_cmd[args]
    run_cmd = perf["record", "-q", "-F", 6249, "-g", run_cmd]

    with local.env(OMP_NUM_THREADS=str(jobs)):
        with track_execution(run_cmd, project, experiment) as run:
            ri = run(retcode=None)

        fg_path = os.path.join(CFG["src_dir"], "extern/FlameGraph")
        if os.path.exists(fg_path):
            sc_perf = local[os.path.join(fg_path, "stackcollapse-perf.pl")]
            flamegraph = local[os.path.join(fg_path, "flamegraph.pl")]

            fold_cmd = ((perf["script"] | sc_perf) > run_f + ".folded")
            graph_cmd = (flamegraph[run_f + ".folded"] > run_f + ".svg")

            fold_cmd()
            graph_cmd()
            persist_perf(ri.db_run, ri.session, run_f + ".svg")
            persist_config(ri.db_run, ri.session, {"cores": str(jobs)})


class PJITperf(pj.PolyJIT):
    """An experiment that uses linux perf tools to generate flamegraphs."""

    NAME = "pj-perf"

    def actions_for_project(self, project):
        from benchbuild.settings import CFG

        project = pj.PolyJIT.init_project(project)

        actns = []
        for i in range(1, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(project)
            cp.run_uuid = uuid.uuid4()
            cp.runtime_extension = ft.partial(run_with_perf, cp, self, CFG, i)
            actns.extend(self.default_runtime_actions(cp))
        return actns
