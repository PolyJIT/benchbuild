#!/usr/bin/env python
"""Database schema for pprof."""

from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pprof.settings import config
from textwrap import dedent

Engine = create_engine("postgresql+psycopg2://{u}:{p}@{h}:{P}/{db}".format(
    u=config["db_user"], h=config["db_host"], P=config["db_port"],
    p=config["db_pass"], db=config["db_name"]))
Session = sessionmaker(bind=Engine)
Base = declarative_base()


class Run(Base):

    """Store a run for each executed test binary."""

    __tablename__ = 'run'

    id = Column(Integer, primary_key=True)
    command = Column(String)
    project_name = Column(String, ForeignKey("project.name"), index=True)
    experiment_name = Column(String, index=True)
    run_group = Column(postgresql.UUID, index=True)
    experiment_group = Column(postgresql.UUID, ForeignKey("experiment.id"), index=True)
    begin = Column(DateTime(timezone=False))
    end = Column(DateTime(timezone=False))
    status = Column(Enum('completed', 'running', 'failed', name = "run_state"))

    def __repr__(self):
        return dedent(
            """<Run(id={0}, command='{1}', project_name='{2}',
                    experiment_name='{3}', run_group='{4}',
                    experiment_group='{5}', begin='{6}', end='{7}')>""".format(
            self.id, self.command, self.project_name, self.experiment_name,
            self.run_group, self.experiment_group, self.begin, self.end)
        )


class RunGroup(Base):
    """ Store information about a run group. """

    __tablename__ = 'rungroup'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True,
                index=True)
    project = Column(String, ForeignKey("project.name"), index=True)
    experiment = Column(postgresql.UUID(as_uuid=True),
                        ForeignKey("experiment.id", ondelete="CASCADE",
                                   onupdate="CASCADE"), index=True)

    begin = Column(DateTime(timezone=False))
    end = Column(DateTime(timezone=False))
    status = Column(Enum('completed', 'running', 'failed', name="run_state"))


class Experiment(Base):

    """Store metadata about experiments."""

    __tablename__ = 'experiment'

    name = Column(String)
    description = Column(String)
    id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    begin = Column(DateTime(timezone=False))
    end = Column(DateTime(timezone=False))

    def __repr__(self):
        return dedent("""<Experiment(name='{0}', description='{1}', begin='{2}',
                              end='{3}')>""".format(
                    self.name, self.description, self.begin, self.end))


class Likwid(Base):

    """Store measurement results of likwid based experiments."""

    __tablename__ = 'likwid'

    metric = Column(String, primary_key=True, index=True)
    region = Column(String, primary_key=True, index=True)
    value = Column(postgresql.DOUBLE_PRECISION)
    core = Column(String, primary_key=True)
    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE", ondelete="CASCADE"),
                    nullable=False,
                    primary_key=True)

    def __repr__(self):
        return dedent(
            """<Likwid(metric='{0}', region='{1}', value={2}, core='{3}',
                   run_id={4})>""".format(
                self.metric, self.region, self.value,
                self.core, self.run_id))


class Metric(Base):

    """Store default metrics, simple name value store."""

    __tablename__ = 'metrics'

    name = Column(String, primary_key=True, index=True, nullable=False)
    value = Column(postgresql.DOUBLE_PRECISION)
    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE", ondelete="CASCADE"),
                    index=True,
                    primary_key=True)

    def __repr__(self):
        return "<Metric(name='{0}', value={1}, run_id='{2}')>".format(self.name, self.value, self.run_id)


class Event(Base):

    """Store PAPI profiling based events."""

    __tablename__ = 'pprof_events'

    name = Column(String, index=True)
    start = Column(postgresql.NUMERIC, primary_key=True)
    duration = Column(postgresql.NUMERIC)
    id = Column(Integer, primary_key=True)
    type = Column(postgresql.SMALLINT)
    tid = Column(postgresql.BIGINT)
    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE", ondelete="CASCADE"),
                    nullable=False,
                    index=True,
                    primary_key=True)

    def __repr__(self):
        return "<Event(name='{0}', start={1}, duration={2}, id={3}, type={4}, run_id={5})>".format(
            self.name, self.start, self.duration, self.id, self.type, self.run_id)


class Project(Base):

    """Store project metadata."""

    __tablename__ = 'project'

    name = Column(String, primary_key=True)
    description = Column(String)
    src_url = Column(String)
    domain = Column(String)
    group_name = Column(String)

    def __repr__(self):
        return "<Project(name='{0}', description='{1}', src_url='{2}', domain'{3}', group_name='{4}')>".format(
            self.name, self.description, self.src_url, self.domain, self.group_name)


class CompileStat(Base):

    """Store compilestats as given by LLVM's '-stats' commoand."""

    __tablename__ = 'compilestats'

    id = Column(postgresql.BIGINT, primary_key=True)
    name = Column(String, index=True)
    component = Column(String, index=True)
    value = Column(postgresql.NUMERIC)
    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE", ondelete="CASCADE"),
                    index=True)

    def __repr__(self):
        return dedent(
            """<CompileStat(name='{0}', component={1}, value={2}, run_id='{3}')>
            """.format(self.name, self.component, self.value, self.run_id))


class RunLog(Base):

    """
    Store log information for every run.

    Properties like, start time, finish time, exit code, stderr, stdout
    are stored here.
    """

    __tablename__ = 'log'

    run_id = Column(Integer, ForeignKey("run.id", onupdate="CASCADE",
                    ondelete="CASCADE"), index=True, primary_key=True)
    begin = Column(DateTime(timezone=False))
    end = Column(DateTime(timezone=False))
    status = Column(Integer)
    config = Column(String)
    stderr = Column(String)
    stdout = Column(String)


class Metadata(Base):

    """
    Store metadata information for every run.

    If you happen to have some free-form data that belongs to the database,
    this is the place for it.
    """

    __tablename__ = "metadata"

    run_id = Column(Integer, ForeignKey("run.id", onupdate="CASCADE",
                    ondelete="CASCADE"), index=True, primary_key=True)
    name = Column(String)
    value = Column(String)


class Config(Base):

    """
    Store customized information about a run.

    You can store arbitrary configuration information about a run here.
    Use it for extended filtering against the run table.
    """

    __tablename__ = 'config'

    run_id = Column(Integer, ForeignKey("run.id", onupdate="CASCADE",
                    ondelete="CASCADE"), index=True, primary_key=True)
    name = Column(String, primary_key=True)
    value = Column(String)

class GlobalConfig(Base):

    """
    Store customized information about a run.

    You can store arbitrary configuration information about a run here.
    Use it for extended filtering against the run table.
    """

    __tablename__ = 'globalconfig'

    experiment_group = Column(postgresql.UUID(as_uuid=True), ForeignKey("experiment.id", onupdate="CASCADE",
                    ondelete="CASCADE"), primary_key=True)
    name = Column(String, primary_key=True)
    value = Column(String)

class RegressionTest(Base):

    """
    Store regression tests for all projects.

    This relation is filled from the PolyJIT side, not from pprof-study.
    We collect all JIT SCoPs found by PolyJIT in this relation for
    regression-test generation.

    """

    __tablename__ = 'regressions'
    run_id = Column(Integer, ForeignKey("run.id", onupdate="CASCADE",
                    ondelete="CASCADE"), index=True, primary_key=True)
    name = Column(String)
    module = Column(String)
    project_name = Column(String)

    def __repr__(self):
        return dedent(
            """<RegressionTest(name='{0}', project_name={1}, module=<omitted>, run_id='{2}')>
            """.format(self.name, self.project_name, self.run_id))

Base.metadata.create_all(Engine, checkfirst=True)
