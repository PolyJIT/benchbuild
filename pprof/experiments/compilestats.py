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
from pprof.experiment import RuntimeExperiment
from pprof.utils.run import partial
from pprof.utils.actions import (Prepare, Build, Download, Configure, Clean,
                                 MakeBuildDir, Echo)

def collect_compilestats(project, experiment, config, clang, **kwargs):
    """Collect compilestats."""
    from pprof.utils.run import guarded_exec, handle_stdin
    from pprof.settings import CFG as c
    from pprof.utils.db import persist_compilestats
    from pprof.utils.run import handle_stdin
    from pprof.utils.schema import CompileStat

    c.update(config)
    clang = handle_stdin(clang["-mllvm", "-stats"], kwargs)

    with local.env(PPROF_ENABLE=0):
        with guarded_exec(clang, project, experiment) as run:
            ri = run()

    if retcode == 0:
        stats = []
        for stat in get_compilestats(ri['stderr']):
            compile_s = CompileStat()
            compile_s.name = stat["desc"].rstrip()
            compile_s.component = stat["component"].rstrip()
            compile_s.value = stat["value"]
            stats.append(compile_s)

        components = c["cs"]["components"].value()
        if components is not None:
            stats = [ s for s in stats if str(s.component) in components]
        names = c["cs"]["names"].value()
        if names is not None:
            stats = [ s for s in stats if str(s.name) in names]

        persist_compilestats(ri['db_run'], ri['session'], stats)


class CompilestatsExperiment(RuntimeExperiment):
    """The compilestats experiment."""

    NAME = "cs"

    def actions_for_project(self, p):
        from pprof.settings import CFG

        p.compiler_extension = partial(collect_compilestats, p, self, CFG)

        actns = [
            MakeBuildDir(p),
            Echo("{}: Configure...".format(self.name)),
            Prepare(p),
            Download(p),
            Configure(p),
            Echo("{}: Building...".format(self.name)),
            Build(p),
            Clean(p)
        ]
        return actns


class PollyCompilestatsExperiment(RuntimeExperiment):
    """The compilestats experiment with polly enabled."""

    NAME = "p-cs"

    def actions_for_project(self, p):
        from pprof.settings import CFG

        llvm_libs = os.path.join(str(CFG["llvm"]["dir"]), "lib")
        p.ldflags = ["-L" + llvm_libs]
        p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolly.so",
                    "-mllvm", "-polly"]
        p.compiler_extension = partial(collect_compilestats, p, self, CFG)

        actns = [
            MakeBuildDir(p),
            Echo("{}: Configure...".format(self.name)),
            Prepare(p),
            Download(p),
            Configure(p),
            Echo("{}: Building...".format(self.name)),
            Build(p),
            Clean(p)
        ]
        return actns



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
