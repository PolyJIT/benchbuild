"""
The 'compilestats' Experiment.

This experiment is a basic experiment in the pprof study. It simply runs
all projects after compiling it with -O3 and catches all statistics emitted
by llvm

"""

from pprof.experiment import step, substep, RuntimeExperiment
from os import path

class CompilestatsExperiment(RuntimeExperiment):
    """The compilestats experiment."""

    NAME = "stats"

    def extra_ldflags(self):
        return []

    def extra_cflags(self):
        return ["-O3"]

    def run_project(self, p):
        """Compile & Run the experiment."""
        from pprof.utils.schema import CompileStat
        from pprof.settings import config
        from pprof.utils.run import partial

        llvm_libs = path.join(config["llvmdir"], "lib")
        p.ldflags = ["-L" + llvm_libs] + self.extra_ldflags()
        p.cflags = self.extra_cflags()
        with step("Configure Project"):
            p.download()

            def _track_compilestats(project, experiment, config, clang,
                                    **kwargs):
                from pprof.utils import run as r
                from pprof.settings import config as c
                from pprof.utils.db import persist_compilestats
                from pprof.utils.run import handle_stdin

                c.update(config)
                clang = handle_stdin(clang["-mllvm", "-stats"], kwargs)

                run, session, retcode, _, stderr = \
                    r.guarded_exec(clang, project.name, experiment.name, project.run_uuid)

                if retcode == 0:
                    stats = []
                    for stat in get_compilestats(stderr):
                        compile_s = CompileStat()
                        compile_s.name = stat["desc"].rstrip()
                        compile_s.component = stat["component"].rstrip()
                        compile_s.value = stat["value"]
                        stats.append(compile_s)
                    persist_compilestats(run, session, stats)

            p.compiler_extension = partial(_track_compilestats, p, self,
                                           config)
            p.configure()
        with step("Build Project"):
            p.build()


def get_compilestats(prog_out):
    """ Get the LLVM compilation stats from :prog_out:. """
    from parse import compile

    stats_pattern = compile("{value:d} {component} - {desc}\n")

    for line in prog_out.split("\n"):
        res = stats_pattern.search(line + "\n")
        if res is not None:
            yield res
