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

from benchbuild.experiment import Experiment
from benchbuild.settings import CFG
from benchbuild.utils.actions import (Build, Clean, Configure, Download, Echo,
                                      MakeBuildDir, Prepare, Run)
from benchbuild.utils.db import (persist_compilestats, persist_config,
                                 persist_time)
from benchbuild.utils.run import track_execution, handle_stdin
LOG = logging.getLogger()


def timing_extension(project, experiment, config, run_f, *args, **kwargs):
    """
    Collect the time measurement.

    Args:
        project: The benchbuild project that called for this measurement.
        experiment: The benchbuild experiment this function is operating under.
        config: The benchbuild configuration used for the current run.
        run_f: The file that gets executed.
        *args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with further keyword arguments. The following
            entries are supported:
            project_name: The real name of the project, that might differ from
                the configured one.
            may_wrap: Signals if a project is suitable for wrapping.
    """
    from benchbuild.utils.cmd import time
    from benchbuild.utils.run import fetch_time_output
    CFG.update(config)
    project.name = kwargs.get("project_name", project.name)
    may_wrap = kwargs.get("may_wrap", True)
    run_config = kwargs.get("run_config", None)
    timing_tag = "BB-Time: "

    run_cmd = local[run_f]
    run_cmd = run_cmd[args]
    if may_wrap:
        run_cmd = time["-f", timing_tag + "%U-%S-%e", run_cmd]

    def handle_timing(run_info):
        """Takes care of the formating for the timing statistics."""
        if may_wrap:
            timings = fetch_time_output(
                timing_tag, timing_tag + "{:g}-{:g}-{:g}",
                run_info.stderr.split("\n"))
            if timings:
                persist_time(run_info.db_run, run_info.session, timings)
            else:
                LOG.info("No timing information found.")
        return run_info

    with track_execution(run_cmd, project, experiment, **kwargs) as run:
        run_info = handle_timing(run())
        if run_config is not None:
            persist_config(run_info.db_run, run_info.session, run_config)
    return run_info

def compilestats_ext(project, experiment, config, clang, **kwargs):
    """
    Collect compilestats and write them to the database.

    Args:
        project: The benchbuild project that called for this measurement.
        experiment: The benchbuild experiment this function is operating under.
        config: The benchbuild configuration used for the current run.
        clang: The clang used for compiling.
        **kwargs: Dictionary with further keyword arguments.
    """
    from benchbuild.experiments.compilestats import get_compilestats
    from benchbuild.utils.schema import CompileStat
    CFG.update(config)
    clang = handle_stdin(clang["-mllvm", "-stats"], kwargs)
    run_config = kwargs.get("run_config", None)

    with local.env(BB_ENABLE=0):
        with track_execution(clang, project, experiment) as run:
            run_info = run()
            if run_config is not None:
                persist_config(run_info.db_run, run_info.session, run_config)

    if run_info.retcode == 0:
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
            LOG.info("No compilestats collected.")
    else:
        LOG.info("There was an error while compiling.")


class PollyTest(Experiment):
    """
    An experiment that executes projects with different configurations.

    The time and the compilestats are collected.
    """
    NAME = "pollytest"

    def actions_for_project(self, p):
        def actions(project):
            """Extends the actions for each single configuration."""
            return [
                MakeBuildDir(project),
                Echo("Compiling... {}".format(project.name)),
                Prepare(project),
                Download(project),
                Configure(project),
                Build(project),
                Echo("Running... {}".format(project.name)),
                Run(project),
                Clean(project)
            ]

        actns = []
        p.cflags = ["-Xclang", "-load", "-Xclang", "LLVMPolly.so"]

        newp = copy.deepcopy(p)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + ["-O3"]
        cfg = {
            "cflags": "-O3"
        }
        newp.runtime_extension = partial(timing_extension, p, self, CFG,
                                         run_config=cfg)
        newp.compiler_extension = partial(compilestats_ext, p, self, CFG,
                                          run_config=cfg)
        actns.extend(actions(newp))

        newp = copy.deepcopy(p)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags +  ["-O3", "-mllvm", "-polly"]
        cfg = {
            "cflags": "-O3 -polly"
        }
        newp.runtime_extension = partial(timing_extension, p, self, CFG,
                                         run_config=cfg)
        newp.compiler_extension = partial(compilestats_ext, p, self, CFG,
                                          run_config=cfg)
        actns.extend(actions(newp))

        newp = copy.deepcopy(p)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + \
                      ["-O3", "-mllvm",
                       "-polly", "-mllvm",
                       "-polly-position=before-vectorizer"]
        cfg = {
            "cflags": "-O3 -polly -polly-position=before-vectorizer"
        }
        newp.runtime_extension = partial(timing_extension, p, self, CFG,
                                         run_config=cfg)
        newp.compiler_extension = partial(compilestats_ext, p, self, CFG,
                                          run_config=cfg)
        actns.extend(actions(newp))

        newp = copy.deepcopy(p)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + \
                      ["-O3", "-mllvm",
                       "-polly", "-mllvm",
                       "-polly-process-unprofitable",
                       "-mllvm", "-polly-position=before-vectorizer"]
        cfg = {
            "cflags": "-O3 -polly -polly-position=before-vectorizer "
                      "-polly-process-unprofitable"
        }
        newp.runtime_extension = partial(timing_extension, p, self, CFG,
                                         run_config=cfg)
        newp.compiler_extension = partial(compilestats_ext, p, self, CFG,
                                          run_config=cfg)
        actns.extend(actions(newp))

        newp = copy.deepcopy(p)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + \
                      ["-O3", "-mllvm",
                       "-polly", "-mllvm",
                       "-polly-process-unprofitable"]
        cfg = {
            "cflags": "-O3 -polly -polly-process-unprofitable"
        }
        newp.runtime_extension = partial(timing_extension, p, self, CFG,
                                         run_config=cfg)
        newp.compiler_extension = partial(compilestats_ext, p, self, CFG,
                                          run_config=cfg)
        actns.extend(actions(newp))
        return actns
