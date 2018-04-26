import logging

import sqlalchemy as sa

import benchbuild.experiment as exp
import benchbuild.extensions as ext
import benchbuild.utils.actions as actns
import benchbuild.utils.schema as schema

LOG = logging.getLogger(__name__)

__FILECONTENT__ = sa.Table(
    'filecontents', schema.metadata(),
    sa.Column(
        'experience_id',
        schema.GUID,
        sa.ForeignKey("experiment.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        primary_key=True),
    sa.Column(
        'rungroup_id',
        schema.GUID,
        sa.ForeignKey("rungroup.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        primary_key=True),
    sa.Column('filename', sa.String, nullable=False, primary_key=True),
    sa.Column('content', sa.LargeBinary))


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
    SCHEMA = [__FILECONTENT__]

    def actions_for_project(self, project):
        import copy
        import uuid

        no_pgo_project = copy.deepcopy(project)
        no_pgo_project.run_uuid = uuid.uuid4()
        pgo_project = copy.deepcopy(project)
        pgo_project.run_uuid = uuid.uuid4()

        project.cflags += ["-O3", "-fprofile-generate=./raw-profiles"]
        cfg_inst = {"cflags": project.cflags, "name": "inst"}
        project.compiler_extension = \
            ext.RunWithTimeout(
                ext.RunCompiler(project, self, config=cfg_inst))
        project.runtime_extension = \
            ext.RuntimeExtension(project, self, config=cfg_inst)

        # Still activating pgo for clang pgo optimisation
        no_pgo_project.cflags += [
            "-O3", "-fprofile-use=./raw-profiles", "-mllvm", "-polly",
            "-mllvm", "-stats"
        ]
        cfg_no_pgo = {"cflags": no_pgo_project.cflags, "name": "no-pgo"}
        no_pgo_project.compiler_extension = \
            ext.RunWithTimeout(
                ext.ExtractCompileStats(project, self, config=cfg_no_pgo)
            )

        pgo_project.cflags += [
            "-O3", "-fprofile-use=./raw-profiles", "-mllvm", "-polly",
            "-mllvm", "-polly-pgo-enable"
            "-mllvm", "-stats"
        ]
        cfg_pgo = {"cflags": pgo_project.cflags, "name": "pgo"}
        pgo_project.compiler_extension = \
            ext.RunWithTime(ext.RuntimeExtension(project, self),
                            config=cfg_pgo)

        actions = [
            actns.RequireAll(actions=[
                actns.MakeBuildDir(project),
                actns.Prepare(project),
                actns.Download(project),
                actns.Configure(project),
                actns.Build(project),
                actns.Run(project),
                actns.SaveProfile(project, filename='prog.profdata'),
                actns.Clean(project),
            ]),
            actns.RequireAll(actions=[
                aactns.MakeBuildDir(no_pgo_project),
                actns.Prepare(no_pgo_project),
                actns.Download(no_pgo_project),
                actns.Configure(no_pgo_project),
                actns.Build(no_pgo_project),
                actns.Run(no_pgo_project),
                actns.Clean(no_pgo_project)
            ]),
            actns.RequireAll(actions=[
                actns.MakeBuildDir(pgo_project),
                actns.Prepare(pgo_project),
                actns.Download(pgo_project),
                actns.Configure(pgo_project),
                actns.RetrieveFile(
                    pgo_project,
                    filename="prog.profdata",
                    run_group=project.run_uuid),
                actns.Build(pgo_project),
                actns.Run(pgo_project),
                actns.Clean(pgo_project)
            ])
        ]
        return actions
