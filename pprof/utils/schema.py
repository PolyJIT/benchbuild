#!/usr/bin/env python
"""Database schema for pprof."""

from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
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
    finished = Column(DateTime(timezone=False))
    command = Column(String)
    project_name = Column(String, ForeignKey("project.name"), index=True)
    experiment_name = Column(String, ForeignKey("experiment.name"), index=True)
    run_group = Column(postgresql.UUID, index=True)
    experiment_group = Column(postgresql.UUID, index=True)

    def __repr__(self):
        return dedent(
            """<Run(id={}, command='{}', project_name='{}',
                    experiment_name='{}', run_group='{}',
                    experiment_group='{}')>""".format(
                self.id, self.finished, self.command, self.project_name,
                self.experiment_name, self.run_group, self.experiment_group))


class Experiment(Base):

    """Store metadata about experiments."""

    __tablename__ = 'experiment'

    name = Column(String, primary_key=True)
    description = Column(String)

    def __repr__(self):
        return "<Experiment(name='{}', description='{}')>".format(self.name, self.description)


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
                    nullable=False, primary_key=True)

    def __repr__(self):
        return dedent(
            """<Likwid(metric='{}', region='{}', value={}, core='{}',
                   run_id={})>""".format(
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
                    primary_key=True)

    def __repr__(self):
        return "<Metric(name='{}', value={}, run_id='{}')>".format(self.name, self.value, self.run_id)


class Event(Base):

    """Store PAPI profiling based events."""

    __tablename__ = 'pprof_events'

    name = Column(String)
    start = Column(postgresql.NUMERIC, primary_key=True)
    duration = Column(postgresql.NUMERIC)
    id = Column(Integer, primary_key=True)
    type = Column(postgresql.SMALLINT)
    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE", ondelete="CASCADE"),
                    nullable=False,
                    primary_key=True)

    def __repr__(self):
        return "<Event(name='{}', start={}, duration={}, id={}, type={}, run_id={})>".format(
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
        return "<Project(name='{}', description='{}', src_url='{}', domain'{}', group_name='{}')>".format(
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
                               onupdate="CASCADE", ondelete="CASCADE"))

    def __repr__(self):
        return dedent(
            """<CompileStat(name='{}', component={}, value={}, run_id='{}')>
            """.format(self.name, self.component, self.value, self.run_id))


class RunLog(Base):

    """
    Store log information for every run.

    Properties like, start time, finish time, exit code, stderr, stdout
    are stored here.
    """

    __tablename__ = 'log'

    run_id = Column(Integer, ForeignKey("run.id", onupdate="CASCADE",
                    ondelete="CASCADE"), primary_key=True,
                    )
    begin = Column(DateTime(timezone=False))
    end = Column(DateTime(timezone=False))
    status = Column(Integer)
    config = Column(String)
    stderr = Column(String)
    stdout = Column(String)

Base.metadata.create_all(Engine, checkfirst=True)
