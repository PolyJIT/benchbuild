"""
The 'compilestats' Experiment.

This experiment is a basic experiment in the pprof study. It simply runs
all projects after compiling it with -O3 and catches all statistics emitted
by llvm

"""

import parse
import os
import warnings
from plumbum import local
from pprof.experiment import step, RuntimeExperiment
from pprof.utils.run import partial

def collect_compilestats(project, experiment, config, clang, **kwargs):
    """Collect compilestats."""
    from pprof.utils import run as r
    from pprof.settings import CFG as c
    from pprof.utils.db import persist_compilestats
    from pprof.utils.run import handle_stdin
    from pprof.utils.schema import CompileStat

    c.update(config)
    clang = handle_stdin(clang["-mllvm", "-stats"], kwargs)

    with local.env(PPROF_ENABLE=0):
        run, session, retcode, _, stderr = r.guarded_exec(
            clang, project.name, experiment.name, project.run_uuid)

    if retcode == 0:
        stats = []
        for stat in get_compilestats(stderr):
            compile_s = CompileStat()
            compile_s.name = stat["desc"].rstrip()
            compile_s.component = stat["component"].rstrip()
            compile_s.value = stat["value"]
            stats.append(compile_s)
        persist_compilestats(run, session, stats)


class CompilestatsExperiment(RuntimeExperiment):
    """The compilestats experiment."""

    NAME = "cs"

    def run_project(self, p):
        """
        Args:
            p: The project we run.
        """
        from pprof.settings import CFG

        with local.env(PPROF_ENABLE=1):
            p.compiler_extension = partial(collect_compilestats, p, self, CFG)
            with step("Prepare build directory."):
                p.clean()
                p.prepare()
            with step("Downloading sources."):
                p.download()
            with step("Bulding {}.".format(p.name)):
                p.configure()
                p.build()


class PollyCompilestatsExperiment(RuntimeExperiment):
    """The compilestats experiment with polly enabled."""

    NAME = "p-cs"

    def run_project(self, p):
        """
        Args:
            p: The project we run.
        """
        from pprof.settings import CFG

        llvm_libs = os.path.join(str(CFG["llvm"]["dir"]), "lib")
        p.ldflags = ["-L" + llvm_libs]
        p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolly.so",
                    "-mllvm", "-polly"]

        with local.env(PPROF_ENABLE=1):
            p.compiler_extension = partial(collect_compilestats, p, self, CFG)
            with step("Prepare build directory."):
                p.clean()
                p.prepare()
            with step("Downloading sources."):
                p.download()
            with step("Bulding {}.".format(p.name)):
                p.configure()
                p.build()


def get_compilestats(prog_out):
    """ Get the LLVM compilation stats from :prog_out:. """

    class CompileStatsParserError(RuntimeWarning):
        pass

    stats_pattern = parse.compile("{value:d} {component} - {desc}\n")

    for line in prog_out.split("\n"):
        if line:
            try:
                res = stats_pattern.search(line + "\n")
            except ValueError as e:
                warnings.warn("Triggered a parser exception for: '" + line +
                              "'\n", CompileStatsParserError)
                res = None
            if res is not None:
                yield res
