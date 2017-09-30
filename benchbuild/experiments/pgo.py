import logging
import benchbuild.utils.actions as actns
import benchbuild.experiment as exp
import benchbuild.extensions as ext
import benchbuild.settings as settings


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
        action_registerprofile = self.default_runtime_actions(project)
        action_registerprofile.insert(-1, actns.SaveProfile(project))
        actions.append(actns.RequireAll(action_registerprofile))

        actns_nopgo = self.default_runtime_actions(no_pgo_project)
        actns_nopgo.insert(3, actns.RetrieveFile(project, "prog.profdata"))
        actions.append(actns.RequireAll(actns_nopgo))

        actns_pgo = self.default_runtime_actions(pgo_project)
        actns_pgo.insert(3, actns.RetrieveFile(project, "prog.profdata"))
        actions.append(actns.RequireAll(actns_pgo))

        return actions
