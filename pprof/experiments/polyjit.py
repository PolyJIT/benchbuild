#!/usr/bin/env python
# encoding: utf-8
"""
The 'polyjit' experiment.

This experiment uses likwid to measure the performance of all binaries
when running with polyjit support enabled.
"""
from pprof.experiments.compilestats import get_compilestats
from pprof.experiment import step, substep, RuntimeExperiment
from pprof.settings import config
from pprof.utils.schema import CompileStat

from plumbum import local
from os import path


class PolyJIT(RuntimeExperiment):

    """The polyjit experiment."""

    def run_step_compilestats(self, p):
        """ Compile the project and track the compilestats. """
        with step("Track Compilestats @ -O3"):
            p.clean()
            p.prepare()
            p.download()
            with substep("Configure Project"):
                def track_compilestats(cc, **kwargs):
                    from pprof.utils import run as r
                    from pprof.utils.db import persist_compilestats
                    from pprof.utils.run import handle_stdin

                    new_cc = handle_stdin(cc["-mllvm", "-stats"], kwargs)

                    run, session = r.begin(new_cc, p.name, self.name,
                                           p.run_uuid)
                    retcode, stdout, stderr = r.guarded_exec(new_cc)

                    if retcode == 0:
                        stats = []
                        for stat in get_compilestats(stderr):
                            c = CompileStat()
                            c.name = stat["desc"].rstrip()
                            c.component = stat["component"].rstrip()
                            c.value = stat["value"]
                            stats.append(c)
                        persist_compilestats(run, session, stats)
                    r.end(run, session, stdout, stderr)

                p.compiler_extension = track_compilestats
                p.configure()

            with substep("Build Project"):
                p.build()

    def run_step_jit(self, p):
        """Run the experiment without likwid."""
        with step("JIT, no instrumentation"):
            p.clean()
            p.prepare()
            p.download()
            with substep("Build"):
                p.configure()
                p.build()
            with substep("Execute {}".format(p.name)):
                def run_with_time(run_f, args, **kwargs):
                    from pprof.utils import run as r
                    from pprof.utils.db import persist_time
                    from plumbum.cmd import time

                    project_name = kwargs.get("project_name", p.name)
                    timing_tag = "PPROF-JIT: "

                    run_cmd = time["-f", timing_tag + "%U-%S-%e", run_f]
                    run_cmd = r.handle_stdin(run_cmd[args], kwargs)

                    run, session = r.begin(str(run_cmd), project_name,
                                           self.name, p.run_uuid)

                    retcode, stdout, stderr = r.guarded_exec(run_cmd)
                    timings = r.fetch_time_output(
                        timing_tag, timing_tag + "{:g}-{:g}-{:g}",
                        stderr.split("\n"))
                    if len(timings) == 0:
                        return

                    persist_time(run, session, timings)
                    r.end(run, session, stdout, stderr)
                p.run(run_with_time)

    def run_step_likwid(self, p):
        """Run the experiment with likwid."""
        from pprof.settings import config
        def run_with_likwid(run_f, args, **kwargs):
            from pprof.utils import run as r
            from pprof.utils.db import persist_likwid
            from pprof.likwid import get_likwid_perfctr
            from plumbum.cmd import rm
            from uuid import uuid4

            project_name = kwargs.get("project_name", p.name)
            likwid_f = p.name + ".txt"

            for group in ["CLOCK"]:
                likwid_path = path.join(config["likwiddir"], "bin")
                likwid_perfctr = local[
                    path.join(likwid_path, "likwid-perfctr")]
                for i in range(int(config["jobs"])):
                    with substep("{} cores & uuid {}".format(i+1, p.run_uuid)):
                        run_cmd = \
                            likwid_perfctr["-O", "-o", likwid_f, "-m",
                                           "-C", "0-{:d}".format(i),
                                           "-g", group, run_f]
                        run_cmd = r.handle_stdin(run_cmd[args], kwargs)

                        run, session = r.begin(run_cmd, project_name,
                                               self.name, p.run_uuid)

                        retcode, stdout, stderr = r.guarded_exec(run_cmd)

                        likwid_measurement = get_likwid_perfctr(likwid_f)
                        """ Use the project_name from the binary, because we
                            might encounter dynamically generated projects.
                        """
                        persist_likwid(run, session, likwid_measurement)
                        r.end(run, session, stdout, stderr)
                        rm("-f", likwid_f)
                        p.run_uuid = uuid4()

        with step("JIT, likwid"):
            p.clean()
            p.prepare()
            p.download()
            p.cflags = ["-DLIKWID_PERFMON"] + p.cflags

            with substep("Build"):
                p.configure()
                p.build()
            with substep("Execute {}".format(p.name)):
                p.run(run_with_likwid)

    def run_project(self, p):
        """
        Execute the pprof experiment.

        We perform this experiment in 2 steps:
            1. with likwid disabled.
            2. with likwid enabled.
        """
        p.ldflags = ["-lpjit", "-lgomp"]

        ld_lib_path = filter(None, config["ld_library_path"].split(":"))
        p.ldflags = ["-L" + el for el in ld_lib_path] + p.ldflags
        p.cflags = ["-Rpass=\"polyjit*\"",
                    "-Xclang", "-load",
                    "-Xclang", "LLVMPolyJIT.so",
                    "-O3",
                    "-mllvm", "-jitable",
                    "-mllvm", "-polly-delinearize=false",
                    "-mllvm", "-polly-detect-keep-going",
                    "-mllvm", "-polli"]
        with local.env(PPROF_ENABLE=0):
            self.run_step_likwid(p)
            self.run_step_jit(p)
            self.run_step_compilestats(p)
