"""
A test experiment for PolyJIT.

This experiment is used to test the analysis of sequences.
"""
import logging
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

        p = PolyJIT.init_project(p)

        actions = []
        p.cflags = ["-03", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                    "-mllvm", "-polly"]
        p.run_uuid = uuid.uuid4()
        jobs = int(CFG["jobs"].value())
        p.compiler_extension = partial(sequence_func,
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

def sequence_func(project, experiment, config, clang, **kwargs):
    """
    Generate the sequence for Polly.

    Args:
        project: The benchbuild.project.
        experiment: The benchbuild.experiment.
        config: The benchbuild.settings.config.
        clang: Plumbum command that executes clang.
        **kwargs: Dictonary with keyword args. The following entries are
            supported:

            project_name: The real name of the project. This might differ from
                the configured project name if the projectgot wrapped with
                ::benchbuild.project.wrap_dynamic.
            has_stdin: Signals whether the stdin should be handled.
    """
    from benchbuild.utils.run import guarded_exec, handle_stdin
    from benchbuild.settings import CFG as c
    from benchbuild.utils.db import persist_compilestats
    from benchbuild.utils.schema import CompileStat
    from benchbuild.experiments.compilestats import get_compilestats

    c.update(config)
    clang = handle_stdin(clang["-mllvm", "-stats"], kwargs)

    with local.env(BB_ENABLE=0):
        with guarded_exec(clang, project, experiment) as run:
            ri = run()

    if ri.retcode == 0:
        stats = []
        for stat in get_compilestats(ri.stderr):
            compile_s = CompileStat()
            compile_s.name = stat["desc"].rstrip()
            compile_s.component = stat["component"].rstrip()
            compile_s.value = stat["value"]
            stats.append(compile_s)

        components = c["cs"]["names"].value()
        if components is not None:
            stats = [s for s in stats if str(s.component) in components]
        names = c["cs"]["names"].value()
        if names is not None:
            stats = [s for s in stats if str(s.name) in names]

        log = logging.getLogger()
        log.info("{:s} results for projects {:s}:".format(experiment.NAME,
                                                          project.NAME))
        log.info("=========================================================\n")
        for stat in stats:
            log.info("{:s} - {:s}".format(str(stat.name), str(stat.value)))
        log.info("=========================================================\n")
        persist_compilestats(ri.db_run, ri.session, stats)
