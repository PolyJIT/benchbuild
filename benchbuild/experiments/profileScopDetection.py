"""
This experiment instruments the parent if any given SCoP and prints the reason
why the parent is not part of the SCoP.
"""
import benchbuild.experiment as exp
import benchbuild.extensions as ext
import benchbuild.experiments.polyjit as pj

import copy
import functools as ft
import glob
import logging
import uuid
import os
from plumbum import local

from benchbuild.utils.run import track_execution
from benchbuild.experiments.polyjit import ClearPolyJITConfig,\
        EnableJITDatabase, EnablePolyJIT, RegisterPolyJITLogs, RequireAll, Any
from benchbuild.extensions import Extension

LOG = logging.getLogger(__name__)

def persist_scopinfos(run, invalidReason, count):
    """Persists the given information"""
    from benchbuild.utils import schema as s
    session = run.session
    session.add(s.ScopDetection(
        run_id=run.db_run.id, invalid_reason=invalidReason, count=count))


class RunWithPprofExperiment(Extension):
    """Write data of profileScopDetection into the database"""
    def __call__(self, *args, **kwargs):
        return self.call_next(*args, **kwargs)


class EnableProfiling(pj.PolyJITConfig, ext.Extension):
    """Adds options for enabling profiling of SCoPs"""
    def __call__(self, *args, **kwargs):
        ret = None
        with self.argv(PJIT_ARGS="-polli-db-execute-atexit"):
            with local.env(PJIT_ARGS=self.value_to_str('PJIT_ARGS')):
                ret = self.call_next(*args, **kwargs)
        return ret

class CaptureProfilingDebugOutput(ext.Extension):
    """Capture the output of the profiling pass and persist it"""
    def __init__(self, *extensions, project=None, experiment=None, **kwargs):
        super(CaptureProfilingDebugOutput, self).__init__(*extensions, **kwargs)
        self.project = project
        self.experiment = experiment

    def __call__(self, *args, **kwargs):
        def handle_profileScopDetection(run_infos):
            """
            Takes care of writing the information of profileScopDetection into
            the database.
            """
            from benchbuild.utils import schema as s
            from parse import compile

            instrumentedPattern = compile("{} [info] Instrumented SCoPs: {:d}")
            notInstrumentedPattern = compile("{} [info] Not instrumented SCoPs: {:d}")
            invalidReasonPattern = compile("{} [info] {} is invalid because of: {}")

            instrumentedCounter = 0
            notInstrumentedCounter = 0;
            invalidReasons = {}

            paths = glob.glob(os.path.join(
                os.path.realpath(os.path.curdir), "profileScops.log"))
            for path in paths:
                file = open(path, 'r')
                for line in file:
                    data = instrumentedPattern.parse(line)
                    if data is not None:
                        instrumentedCounter+=data[1]
                        continue

                    data = notInstrumentedPattern.parse(line)
                    if data is not None:
                        notInstrumentedCounter += data[1]
                        continue

                    data = invalidReasonPattern.parse(line)
                    if data is not None:
                        reason = data[2]
                        if reason not in invalidReasons:
                            invalidReasons[reason] = 0
                        invalidReasons[reason]+=1

            session = s.Session()
            for reason in invalidReasons:
                persist_scopinfos(run_infos[0], reason, invalidReasons[reason])

            session.commit()

            print("Instrumented SCoPs: ", instrumentedCounter)
            print("Not instrumented SCoPs: ", notInstrumentedCounter)

            return run_infos

        res = self.call_next(*args, **kwargs)
        return handle_profileScopDetection(res)


class PProfExperiment(exp.Experiment):
    """This experiment instruments the parent if any given SCoP and prints the
    reason why the parent is not part of the SCoP."""

    NAME = "profileScopDetection"

    def actions_for_project(self, project):
        from benchbuild.settings import CFG

        actns = []

        project.cflags = ["-Xclang", "-load", "-Xclang", "LLVMPolly.so",
                "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                "-O3",
                "-mllvm", "-polli-profile-scops"]
        project.ldflags = ["-lpjit"]
        project.compiler_extension = CaptureProfilingDebugOutput(
                ext.RuntimeExtension(project, self),
                project=project, experiment=self)

        pjit_extension = \
                ClearPolyJITConfig(
                        EnableJITDatabase(
                            EnableProfiling(
                                RunWithPprofExperiment(
                                    ext.RuntimeExtension(project, self,
                                        config={"jobs": 1,
                                            "name": "profileScopDetection"
                                            }
                                        ),
                                    config={"jobs": 1}
                                    ),
                                project=project),
                            project=project)
                        )
                project.runtime_extension = \
                        ext.LogAdditionals(
                                RegisterPolyJITLogs(
                                    ext.RunWithTime(pjit_extension)
                                    )
                                )
                        return self.default_runtime_actions(project)
