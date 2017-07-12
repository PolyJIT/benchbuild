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

    def actions_for_project(self, project):
        actns = []
        project.cflags = ["-Xclang", "-load", "-Xclang", "LLVMPolly.so"]

        newp = copy.deepcopy(project)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + ["-O3"]
        cfg = {
            "name": "-O3"
        }
        newp.compiler_extension = ExtractCompileStats(newp, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))

        newp = copy.deepcopy(project)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + ["-O3", "-mllvm", "-polly"]
        cfg = {
            "name": "-O3 -polly"
        }
        newp.compiler_extension = ExtractCompileStats(newp, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))

        newp = copy.deepcopy(project)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + [
           "-O3", "-mllvm",
           "-polly", "-mllvm",
           "-polly-position=before-vectorizer"]
        cfg = {
            "name": "-O3 -polly -polly-position=before-vectorizer"
        }
        newp.compiler_extension = ExtractCompileStats(newp, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))

        newp = copy.deepcopy(project)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + [
           "-O3", "-mllvm",
           "-polly", "-mllvm",
           "-polly-process-unprofitable",
           "-mllvm", "-polly-position=before-vectorizer"]
        cfg = {
            "name": "-O3 -polly -polly-position=before-vectorizer "
                    "-polly-process-unprofitable"
        }
        newp.compiler_extension = ExtractCompileStats(newp, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))

        newp = copy.deepcopy(project)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + [
           "-O3", "-mllvm",
           "-polly", "-mllvm",
           "-polly-process-unprofitable"]
        cfg = {
            "name": "-O3 -polly -polly-process-unprofitable"
        }
        newp.compiler_extension = ExtractCompileStats(newp, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))
        return actns
