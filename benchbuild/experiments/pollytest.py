"""
The 'pollytest' experiment.

This experiment uses four different configs to analyse the compilestats' and the
time's behavior regarding the position of polly and unprofitable processes.
"""
import copy
import logging
import uuid

from functools import partial
from plumbum import local

from benchbuild.utils.actions import (Build, Clean, Configure, Download, Echo,
                                      MakeBuildDir, Prepare, Run)
from benchbuild.utils.cmd import time
from benchbuild.experiments.compilestats import get_compilestats
from benchbuild.experiments.polyjit import PolyJIT

def time_and_compilestats(project, experiment, config,
                          jobs, run_f, *args, **kwargs):
    """
    Collect both time measurement and compilestats of the clang cmd.

    Args:
        project: The benchbuild project that called for this measurement.
        experiment: The benchbuild experiment this function is operating under.
        config: The benchbuild configuration used for the current run.
        jobs: The number of cores the run is allowed to use.
        run_f: The file that gets executed.
        *args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with further keyword arguments. The following
            entries are supported:
            project_name: The real name of the project, that might differ from
                the configured one.
            may_wrap: Signals if a project is suitable for wrapping.
    """
    from benchbuild.utils.run import track_execution, fetch_time_output
    from benchbuild.settings import CFG
    from benchbuild.utils.db import (persist_compilestats, persist_config,
                                     persist_time)
    from benchbuild.utils.schema import CompileStat
    CFG.update(config)
    project.name = kwargs.get("project_name", project.name)
    may_wrap = kwargs.get("may_wrap", True)
    timing_tag = "BB-Time: "
    log = logging.getLogger()

    run_cmd = local[run_f]
    run_cmd = run_cmd[args]
    if may_wrap:
        run_cmd = time["-f", timing_tag + "%U-%S-%e", run_cmd]

    def handle_compilestats(run_info):
        """Handles the compiler infos and stores them to the database."""
        stats = []
        for stat in get_compilestats(run_info.stderr):
            compile_s = CompileStat()
            compile_s.name = stat["desc"].rstrip()
            compile_s.component = stat["component"].rstrip()
            compile_s.value = stat["value"]
            stats.append(compile_s)

        components = CFG["cs"]["components"].value()
        if components is not None:
            stats = [s for s in stats if str(s.component) in components]
        names = CFG["cs"]["names"].value()
        if names is not None:
            stats = [s for s in stats if str(s.name) in names]
        if stats:
            persist_compilestats(run_info.db_run, run_info.session, stats)
        else:
            log.info("No compilestats collected.")

    def handle_timing(run_info):
        """Handles the timing stats and writes them to the database."""
        if may_wrap:
            timings = fetch_time_output(
                timing_tag, timing_tag + "{:g}-{:g}-{:g}",
                run_info.stderr.split("\n"))
            if timings:
                persist_time(run_info.db_run, run_info.session, timings)
            else:
                log.info("No timing information found.")

    def handle_infos(run_info):
        """Combines compilestats and timing in one experiment."""
        if run_info.retcode == 0:
            handle_compilestats(run_info)
            handle_timing(run_info)
        else:
            log.error("The run seems to have failed.")
        return run_info

    with track_execution(run_cmd, project, experiment, **kwargs) as run:
        run_info = handle_infos(run())
    persist_config(run_info.db_run, run_info.session, {"cores":str(jobs)})
    return run_info


class PollyTest(PolyJIT):
    """
    An experiment that executes projects with different configurations.

    The time and the compilestats are collected.
    """
    NAME = "pollytest"

    def actions_for_project(self, p):
        from benchbuild.settings import CFG

        def extend_actions(actions, project):
            """Extends the actions for each single configuration."""
            actions.extend([
                MakeBuildDir(project),
                Echo("Compiling... {}".format(project.name)),
                Prepare(project),
                Download(project),
                Configure(project),
                Build(project),
                Echo("Running... {}".format(project.name)),
                Run(project),
                Clean(project)
            ])
            return actions

        def make_copies(amount):
            """
            Create copies of the projects so each configuration can be analyzed
            according to the project's run id.
            """
            copies = []
            for _ in range(amount):
                new_project = copy.deepcopy(p)
                new_project.run_uuid = uuid.uuid4()
                new_project.runtime_extension = partial(time_and_compilestats,
                                                        new_project,
                                                        self,
                                                        CFG,
                                                        CFG["jobs"].value())
                copies.append(new_project)
            return copies

        p = PolyJIT.init_project(p)
        actns = []
        num_configs = 5
        projects = make_copies(num_configs)

        prj = projects.pop()
        prj.cflags = ["-O3"]
        actns = extend_actions(actns, prj)

        prj = projects.pop()
        prj.cflags = ["-O3", "-mllvm", "-polly"]
        actns = extend_actions(actns, prj)

        prj = projects.pop()
        prj.cflags = ["-O3", "-mllvm",
                      "-polly", "-mllvm",
                      "-polly-position=before-vectorize"]
        actns = extend_actions(actns, prj)

        prj = projects.pop()
        prj.cflags = ["-O3", "-mllvm",
                      "-polly", "-mllvm",
                      "-polly-process-unprofitable"]
        actns = extend_actions(actns, prj)

        prj = projects.pop()
        prj.cflags = ["-O3", "-mllvm",
                      "-polly", "-mllvm",
                      "-polly-process-unprofitable",
                      "-mllvm", "-polly-position=before-vectorize"]
        actns = extend_actions(actns, prj)

        return actns
