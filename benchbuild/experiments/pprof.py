"""
The 'pprof' Experiment.

TODO Description
"""
import logging

from benchbuild.experiment import Experiment
from benchbuild.utils.actions import (Prepare, Build, Download, Configure,
                                      Clean, MakeBuildDir, Run, Echo)
from benchbuild.utils.run import track_execution, fetch_time_output
from benchbuild.utils.db import persist_time, persist_config
from benchbuild.utils.cmd import time

from benchbuild.settings import CFG
from functools import partial
from plumbum import local


def RunInstrumented(project, experiment, run_f, *args, **kwargs):
    command = local[run_f]
    with track_execution(command, project, experiment) as run:
        ri = run()

    return ri

class PProfExperiment(Experiment):
    """The pprof experiment with fancy description."""

    NAME = "pprof"

    def actions_for_project(self, project):
        #project.cflags = ["-Xclang", "-load", "-Xclang", "libpjit.so", "-Xclang", "-load", "-Xclang", "LLVMPprof.so", "/home/stefan/PolyJIT_Build/polli-prefix/src/polli-build/lib/libpjit.so"] #Use -O3?
        #project.ldflags = ["-lpprof"]
        project.cflags = ["-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so", "/home/stefan/PolyJIT_Install/lib/libpjit.so"]
        project.runtime_extension = partial(RunInstrumented, project, self)
        actns = [
            MakeBuildDir(project),
            Echo("Compiling... {}".format(project.name)),
            Prepare(project),
            Download(project),
            Configure(project),
            Build(project),
            Echo("Running... {}".format(project.name)),
            Run(project),
            Clean(project),
        ]
        return actns
