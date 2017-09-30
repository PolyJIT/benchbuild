import logging
import benchbuild.utils.actions as actns
import benchbuild.experiment as exp
import benchbuild.extensions as ext
import benchbuild.settings as settings

from benchbuild.utils.cmd import llvm_profdata

LOG = logging.getLogger(__name__)


class PGO(exp.Experiment):
    """
    Evaluate Luc Forget's implementation of a loop profile tree.

    The experiment compiles every project three times:
        1. Instrument with profile counters.
        2. Without PGO
        3. With PGO

        Execution proceeds as follows:
            INST: Generate & Run a sub-experiment that stores
                  the profiling information in the database.
            NO-PGO: Compile and Run the project (wrapped with time).
            PGO:    Compile and Run the project (using profiling information
                    from the database, INST).
    """
    NAME = "pgo"

    def actions_for_project(self, project):
        import copy
        import uuid

        no_pgo_project = copy.deepcopy(project)
        no_pgo_project.run_uuid = uuid.uuid4()
        pgo_project = copy.deepcopy(project)
        pgo_project.run_uuid = uuid.uuid4()

        project.cflags += [
            "-O3",
            "-fprofile-instr-generate=prog.profraw"
        ]
        cfg_inst = {
            "cflags": project.cflags,
            "name": "inst"
        }
        project.compiler_extension = \
            ext.RuntimeExtension(project, self, config=cfg_inst)

        # Still activating pgo for clang pgo optimisation
        no_pgo_project.cflags += [
            "-O3",
            "-fprofile-instr-use=prog.profdata",
            "-mllvm", "-polly",
            "-mllvm", "-stats"
        ]
        cfg_no_pgo = {
            "cflags": no_pgo_project.cflags,
            "name": "no-pgo"
        }
        no_pgo_project.compiler_extension = \
            ext.RunWithTimeout(
                ext.ExtractCompileStats(project, self, config=cfg_no_pgo)
            )

        pgo_project.cflags += [
            "-O3",
            "-fprofile-instr-use=prog.profdata",
            "-mllvm", "-polly",
            "-mllvm", "-polly-pgo-enable"
            "-mllvm", "-stats"
        ]
        cfg_pgo = {
            "cflags": pgo_project.cflags,
            "name": "pgo"
        }
        pgo_project.compiler_extension = \
            ext.RunWithTime(ext.RuntimeExtension(project, self))

        actions = []
        actions.append(actns.RequireAll(
            self.default_runtime_actions(project)))
        actions.insert(-1, SaveProfile(project))

        actns_nopgo = actns.RequireAll(
            self.default_runtime_actions(no_pgo_project))
        actns_nopgo.insert(3, RetrieveFile(project, "prog.profdata"))
        actions.append(actns_nopgo)

        actns_pgo = actns.RequireAll(self.default_runtime_actions(pgo_project))
        actns_pgo.insert(3, RetrieveFile(project, "prog.profdata"))
        actions.append(actns_pgo)

        return actions

class SaveProfile(actns.Step): 
    NAME = "SAVEPROFILE"
    DESCRIPTION = "Save a profile in llvm format in the DB"

    def __init__(self, project_or_experiment):
        super(SaveProfile, self).__init__(project_or_experiment, None)

    @notify_step_begin_end
    def __call__(self): 
        obj_builddir = self._obj.builddir
        rawprofile = os.path.abs_path(obj_builddir / "prog.profraw")
        processed_profile = obj_builddir / "prog.profdata"
        llvm_profdata("merge", 
                        "-output={}".format(rawprofile),
                        os.path.abs_path(processed_profile))
        from benchbuild.utils.db import create_and_persist_file
        create_and_persist_file("prog.profdata", 
                                processed_profile,
                                self._obj)
        self.status = actns.StepResult.OK

class RetrieveFile(actns.Step):
    def __init__(self, project_or_experiment, filename):
        super(RetrieveFile, self).__init__(project_or_experiment, None)
        self.filename = filename

    @notify_step_begin_end
    def __call__(self):
        rep = self._obj.builddir
        from benchbuild.utils.db import extract_file
        extract_file(self.filename, rep, self._obj)
        self.status = actns.StepResult.OK
