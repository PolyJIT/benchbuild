import copy
from functools import partial

import benchbuild.extensions as ext
import benchbuild.experiments.polyjit as pj

from plumbum import local


def run_with_papi(project, experiment, config, jobs, run_f, args, **kwargs):
    """
    Run the given file with PAPI support.

    This just runs the project as PAPI support should be compiled in
    already. If not, this won't do a lot.

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
    from benchbuild.utils.db import persist_config

    CFG.update(config)
    project.name = kwargs.get("project_name", project.name)
    run_cmd = local[run_f]
    run_cmd = run_cmd[args]

    run_info = None
    with local.env(OMP_NUM_THREADS=jobs):
        with track_execution(run_cmd, project, experiment) as run:
            run_info = run()

    persist_config(run_info.db_run, run_info.session,
                   {"cores": str(jobs)})
    return run_info


class PJITpapi(pj.PolyJIT):
    """
    Experiment that uses PolyJIT's instrumentation facilities.

    This uses PolyJIT to instrument all projects with libPAPI based
    region measurements. In the end the region measurements are
    aggregated and metrics like the dynamic SCoP coverage are extracted.

    This uses the same set of flags as all other PolyJIT based experiments.
    """

    NAME = "pj-papi"

#    FIXME: Check, if pporf_analyze is actually needed anymore.
#    def actions(self):
#        """Do the postprocessing, after all projects are done."""
#        actions = super(PJITpapi, self).actions()
#        from benchbuild.utils.actions import Step
#
#        class Analyze(Step):
#            NAME = "ANALYZE"
#            DESCRIPTION = "Analyze the experiment after completion."
#
#        def run_pprof_analyze():
#            from benchbuild.utils.cmd import pprof_analyze
#
#            with local.env(BB_EXPERIMENT=self.name,
#                           BB_USE_DATABASE=1,
#                           BB_USE_FILE=0,
#                           BB_USE_CSV=0):
#                pprof_analyze()
#
#        actions.append(
#            Analyze(self, run_pprof_analyze)
#        )
#
#        return actions

    def actions_for_project(self, project):
        from benchbuild.settings import CFG

        project = pj.PolyJIT.init_project(project)
        project.cflags = ["-mllvm", "-polli-instrument"] + project.cflags
        project.ldflags = project.ldflags + ["-lpprof"]

        actns = []
        for i in range(1, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(project)
            cp.compiler_extension = ext.ExtractCompileStats(cp, self)
            cp.runtime_extension = partial(run_with_papi, cp, self, CFG, i)
            actns.extend(self.default_runtime_actions(cp))

        return actns
