"""
This experiment instruments the parent if any given SCoP and prints the reason
why the parent is not part of the SCoP.
"""
import benchbuild.experiment as exp
import benchbuild.extensions as ext
import copy
import functools as ft
import logging
import uuid
from plumbum import local

from benchbuild.utils.run import track_execution
from benchbuild.experiments.polyjit import ClearPolyJITConfig,\
        EnableJITDatabase, EnablePolyJIT, RegisterPolyJITLogs, RequireAll, Any
from benchbuild.extensions import Extension

LOG = logging.getLogger(__name__)

def run_with_profilescops(project, experiment, config, jobs, run_f, args, **kwargs):
    print("HERE");

    from benchbuild.settings import CFG
    from benchbuild.utils.run import track_execution, handle_stdin

    CFG.update(config)
    project.name = kwargs.get("project_name", project.name)
    run_cmd = local[run_f]
    print(run_cmd)
    run_cmd = handle_stdin(run_cmd[args], kwargs)
    #run_cmd = perf["record", "-q", "-F", 6249, "-g", run_cmd]

    with track_execution(run_cmd, project, experiment) as run:
        ri = run()

    persist_scopinfos(ri)

def persist_scopinfos(run):
    from benchbuild.utils import schema as s
    LOG.debug("Persist scops for '%s'", run)
    session = run.session
    session.add(s.ScopDetection(
        run_id=run.db_run.id, invalidReason="Not yet implemented", count=-1))


class RunWithPprofExperiment(Extension):
    """Write data of profileScopDetection into the database"""
    def __call__(self, *args, **kwargs):
        from benchbuild.utils.cmd import time

        def handle_profileScopDetection(run_infos):
            """
            Takes care of writing the information of profileScopDetection into
            the database.
            """
            from benchbuild.utils import schema as s

            session = s.Session()
            for run_info in run_infos:
                print("Stderr: " + run_info.stderr)
                print("Stdout: " + run_info.stdout)
                persist_scopinfos(run_info)

            session.commit()
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

        cp = copy.deepcopy(project)
        cp.run_uuid = uuid.uuid4()
        pjit_extension = \
                ClearPolyJITConfig(
                    EnableJITDatabase(
                        EnablePolyJIT(
                            RunWithPprofExperiment(
                                ext.RuntimeExtension(cp, self,
                                    config={"jobs": 1,
                                        "name": "profileScopDetection"
                                        }
                                    ),
                                config={"jobs": 1}
                            ),
                        project=cp),
                    project=cp)
                )
        cp.runtime_extension = \
                ext.LogAdditionals(
                        RegisterPolyJITLogs(
                            ext.RunWithTime(pjit_extension)
                        )
                )
        actns.append(RequireAll(self.default_runtime_actions(cp)))

        return [Any(actns)]
