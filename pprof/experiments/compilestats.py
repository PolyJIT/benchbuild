#!/usr/bin/env python
# encoding: utf-8
"""
The 'compilestats' Experiment.

This experiment is a basic experiment in the pprof study. It simply runs
all projects after compiling it with -O3 and catches all statistics emitted
by llvm

"""

from pprof.experiment import step, substep, RuntimeExperiment
from pprof.settings import config
from os import path
from pprof.utils.schema import CompileStat


class CompilestatsExperiment(RuntimeExperiment):
    """The compilestats experiment."""

    def extra_ldflags(self):
        return []

    def extra_cflags(self):
        return ["-O3"]

    def persist_run(self, cmd, project_name, run_uuid, stats):
        """ Persist the run results in the database."""
        from pprof.utils.db import create_run

        # Do not forget to update the table schema
        run, session = create_run(cmd, project_name, self.name, run_uuid)

        for stat in stats:
            stat.run_id = run.id
            session.add(stat)

        session.commit()

    def run_project(self, p):
        """Compile & Run the experiment."""
        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("Track Compilestats @ -O3"):
            p.ldflags = ["-L" + llvm_libs] + self.extra_ldflags()
            p.cflags = self.extra_cflags()
            with substep("Configure Project"):
                p.download()

                def track_compilestats(cc, **kwargs):
                    from pprof.utils.run import handle_stdin
                    new_cc = handle_stdin(cc["-mllvm", "-stats"], kwargs)

                    retcode, stdout, stderr = new_cc.run()
                    if retcode == 0:
                        stats = []
                        for stat in get_compilestats(stderr):
                            c = CompileStat()
                            c.name = stat["desc"].rstrip()
                            c.component = stat["component"].rstrip()
                            c.value = stat["value"]
                            stats.append(c)
                        self.persist_run(
                            str(new_cc), p.name, p.run_uuid, stats)

                p.compiler_extension = track_compilestats
                p.configure()
            with substep("Build Project"):
                p.build()


def get_compilestats(prog_out):
    """ Get the LLVM compilation stats from :prog_out:. """
    from parse import compile

    stats_pattern = compile("{value:d} {component} - {desc}\n")

    for line in prog_out.split("\n"):
        res = stats_pattern.search(line + "\n")
        if res is not None:
            yield res
