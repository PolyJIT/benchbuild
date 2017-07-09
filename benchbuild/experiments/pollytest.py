"""
The 'pollytest' experiment.

This experiment uses four different configs to analyse the compilestats' and the
time's behavior regarding the position of polly and unprofitable processes.
"""
import copy
import logging
import uuid

from benchbuild.extensions import (RunWithTime, RuntimeExtension,
                                   ExtractCompileStats)
from benchbuild.experiment import Experiment

LOG = logging.getLogger(__name__)


class PollyTest(Experiment):
    """
    An experiment that executes projects with different configurations.

    The time and the compilestats are collected.
    """
    NAME = "pollytest"

    def actions_for_project(self, p):
        actns = []
        p.cflags = ["-Xclang", "-load", "-Xclang", "LLVMPolly.so"]

        newp = copy.deepcopy(p)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + ["-O3"]
        cfg = {
            "cflags": "-O3"
        }

        newp.runtime_extension = RunWithTime(
            RuntimeExtension(p, self, config=cfg))

        newp.compiler_extension = ExtractCompileStats(p, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))

        newp = copy.deepcopy(p)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + ["-O3", "-mllvm", "-polly"]
        cfg = {
            "cflags": "-O3 -polly"
        }
        newp.runtime_extension = RunWithTime(
            RuntimeExtension(p, self, config=cfg))
        newp.compiler_extension = ExtractCompileStats(p, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))

        newp = copy.deepcopy(p)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + [
           "-O3", "-mllvm",
           "-polly", "-mllvm",
           "-polly-position=before-vectorizer"]
        cfg = {
            "cflags": "-O3 -polly -polly-position=before-vectorizer"
        }
        newp.runtime_extension = RunWithTime(
            RuntimeExtension(p, self, config=cfg))
        newp.compiler_extension = ExtractCompileStats(p, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))

        newp = copy.deepcopy(p)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + [
           "-O3", "-mllvm",
           "-polly", "-mllvm",
           "-polly-process-unprofitable",
           "-mllvm", "-polly-position=before-vectorizer"]
        cfg = {
            "cflags": "-O3 -polly -polly-position=before-vectorizer "
                      "-polly-process-unprofitable"
        }
        newp.runtime_extension = RunWithTime(
            RuntimeExtension(p, self, config=cfg))
        newp.compiler_extension = ExtractCompileStats(p, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))

        newp = copy.deepcopy(p)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + [
           "-O3", "-mllvm",
           "-polly", "-mllvm",
           "-polly-process-unprofitable"]
        cfg = {
            "cflags": "-O3 -polly -polly-process-unprofitable"
        }
        newp.runtime_extension = RunWithTime(
            RuntimeExtension(p, self, config=cfg))
        newp.compiler_extension = ExtractCompileStats(p, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))
        return actns
