#!/usr/bin/env python
# encoding: utf-8
"""
The 'polyjit' experiment.

This experiment uses likwid to measure the performance of all binaries
when running with polyjit support enabled.
"""
from pprof.experiment import step, substep, RuntimeExperiment
from pprof.settings import config

from plumbum import local
from os import path


class PolyJIT(RuntimeExperiment):

    """The polyjit experiment."""

    def run_step_jit(self, p):
        """Run the experiment without likwid."""
        with step("JIT, no instrumentation"):
            p.download()
            with substep("Build"):
                p.configure()
                p.build()
            with substep("Execute {}".format(p.name)):
                def run_with_time(run_f, args, **kwargs):
                    from plumbum.cmd import time
                    from pprof.utils.run import fetch_time_output, handle_stdin

                    project_name = kwargs.get("project_name", p.name)
                    timing_tag = "PPROF-JIT: "

                    run_cmd = time["-f", timing_tag + "%U-%S-%e", run_f]
                    run_cmd = handle_stdin(run_cmd[args], kwargs)
                    _, _, stderr = run_cmd.run()

                    timings = fetch_time_output(timing_tag,
                                                timing_tag + "{:g}-{:g}-{:g}",
                                                stderr.split("\n"))
                    if len(timings) == 0:
                        return

                    super(PolyJIT, self).persist_run(str(run_cmd),
                                                     project_name,
                                                     p.run_uuid,
                                                     timings)
                p.run(run_with_time)

    def run_step_likwid(self, p):
        """Run the experiment with likwid."""
        with step("JIT, likwid"):
            p.clean()
            p.prepare()
            p.download()

            with substep("Build"):
                p.configure()
                p.build()
            with substep("Execute {}".format(p.name)):
                from pprof.settings import config

                def run_with_likwid(run_f, args, **kwargs):
                    from pprof.utils.run import handle_stdin
                    from pprof.likwid import get_likwid_perfctr
                    from plumbum.cmd import rm

                    project_name = kwargs.get("project_name", p.name)
                    likwid_f = p.name + ".txt"

                    for group in ["CLOCK", "DATA", "ENERGY"]:
                        likwid_path = path.join(config["likwiddir"], "bin")
                        likwid_perfctr = local[
                            path.join(likwid_path, "likwid-perfctr")]
                        for i in range(int(config["jobs"])):
                            run_cmd = \
                                likwid_perfctr["-O", "-o", likwid_f, "-m",
                                               "-C", "-L:0-{:d}".format(i),
                                               "-g", group, run_f]

                            run_cmd = handle_stdin(run_cmd[args], kwargs)
                            with local.env(OMP_NUM_THREADS=i):
                                run_cmd()

                            likwid_measurement = get_likwid_perfctr(likwid_f)
                            """ Use the project_name from the binary, because we
                                might encounter dynamically generated projects.
                            """
                            self.persist_run(project_name, p.run_uuid,
                                             str(run_cmd), likwid_measurement)
                            rm("-f", likwid_f)
                p.run(run_with_likwid)

    def run_project(self, p):
        """
        Execute the pprof experiment.

        We perform this experiment in 2 steps:
            1. with likwid disabled.
            2. with likwid enabled.
        """
        llvm_libs = path.join(config["llvmdir"], "lib")
        p.ldflags = ["-L" + llvm_libs, "-lpjit", "-lpprof", "-lpapi"]

        ld_lib_path = filter(None, config["ld_library_path"].split(":"))
        p.ldflags = ["-L" + el for el in ld_lib_path] + p.ldflags
        p.cflags = ["-O3",
                    "-Xclang", "-load",
                    "-Xclang", "LLVMPolyJIT.so",
                    "-mllvm", "-polli",
                    "-mllvm", "-polly-parallel",
                    "-mllvm", "-jitable",
                    "-mllvm", "-polly-detect-keep-going"]
        with local.env(PPROF_ENABLE=0):
            self.run_step_jit(p)
            self.run_step_likwid(p)

    def persist_run(self, project_name, group, cmd, measurements):
        """ Persist all likwid results. """
        from pprof.utils import schema as s
        from pprof.utils.db import create_run

        run, session = create_run(str(cmd), project_name, self.name, group)
        for (region, name, core, value) in measurements:
            m = s.Likwid(metric=name, region=region, value=value, core=core,
                         run_id=run.id)
            session.add(m)
        session.commit()
