"""
The 'compilestats' experiment.

This experiment is a basic experiment in the benchbuild study. It simply runs
all projects after compiling it with -O3 and catches all statistics emitted
by llvm.

"""
import sqlalchemy as sa

import benchbuild.extensions as ext
import benchbuild.utils.schema as schema
from benchbuild.experiment import Experiment


class CompileStat(schema.BASE):
    __tablename__ = 'compilestats'

    run_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("run.id", onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
        primary_key=True)
    id = sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True)
    name = sa.Column('name', sa.String, index=True)
    component = sa.Column('component', sa.String, index=True)
    value = sa.Column('value', sa.Numeric)


class CompilestatsExperiment(Experiment):
    """The compilestats experiment."""

    NAME = "cs"
    SCHEMA = [CompileStat.__table__]

    def actions_for_project(self, project):
        project.compiler_extension = \
            ext.RunWithTimeout(ext.ExtractCompileStats(project, self))
        return CompilestatsExperiment.default_compiletime_actions(project)


class PollyCompilestatsExperiment(Experiment):
    """The compilestats experiment with polly enabled."""

    NAME = "p-cs"
    SCHEMA = [CompileStat.__table__]

    def actions_for_project(self, project):
        project.cflags = [
            "-O3", "-Xclang", "-load", "-Xclang", "LLVMPolly.so", "-mllvm",
            "-polly"
        ]
        project.compiler_extension = \
            ext.RunWithTimeout(ext.ExtractCompileStats(project, self))
        return CompilestatsExperiment.default_compiletime_actions(project)
