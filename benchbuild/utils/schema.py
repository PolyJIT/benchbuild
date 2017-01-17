"""Database schema for benchbuild."""

import logging
from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from benchbuild.settings import CFG

BASE = declarative_base()

class Run(BASE):
    """Store a run for each executed test binary."""

    __tablename__ = 'run'

    id = Column(Integer, primary_key=True)
    command = Column(String)
    project_name = Column(String, ForeignKey("project.name"), index=True)
    experiment_name = Column(String, index=True)
    run_group = Column(postgresql.UUID, index=True)
    experiment_group = Column(postgresql.UUID,
                              ForeignKey("experiment.id"),
                              index=True)
    begin = Column(DateTime(timezone=False))
    end = Column(DateTime(timezone=False))
    status = Column(Enum('completed', 'running', 'failed', name="run_state"))

    def __repr__(self):
        return ("<Run: {0} status={1} run={2}>").format(
            self.project_name, self.status, self.id)


class RunGroup(BASE):
    """ Store information about a run group. """

    __tablename__ = 'rungroup'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, index=True)
    project = Column(String, ForeignKey("project.name"), index=True)
    experiment = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("experiment.id",
                   ondelete="CASCADE",
                   onupdate="CASCADE"),
        index=True)

    begin = Column(DateTime(timezone=False))
    end = Column(DateTime(timezone=False))
    status = Column(Enum('completed', 'running', 'failed', name="run_state"))


class Experiment(BASE):
    """Store metadata about experiments."""

    __tablename__ = 'experiment'

    name = Column(String)
    description = Column(String)
    id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    begin = Column(DateTime(timezone=False))
    end = Column(DateTime(timezone=False))

    def __repr__(self):
        return "<Experiment {name}>".format(name=self.name)


class Likwid(BASE):
    """Store measurement results of likwid based experiments."""

    __tablename__ = 'likwid'

    metric = Column(String, primary_key=True, index=True)
    region = Column(String, primary_key=True, index=True)
    value = Column(postgresql.DOUBLE_PRECISION)
    core = Column(String, primary_key=True)
    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    nullable=False,
                    primary_key=True)


class Metric(BASE):
    """Store default metrics, simple name value store."""

    __tablename__ = 'metrics'

    name = Column(String, primary_key=True, index=True, nullable=False)
    value = Column(postgresql.DOUBLE_PRECISION)
    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    index=True,
                    primary_key=True)

    def __repr__(self):
        return "{0} - {1}".format(self.name, self.value)

class Event(BASE):
    """Store PAPI profiling based events."""

    __tablename__ = 'benchbuild_events'

    name = Column(String, index=True)
    start = Column(postgresql.NUMERIC, primary_key=True)
    duration = Column(postgresql.NUMERIC)
    id = Column(Integer, primary_key=True)
    type = Column(postgresql.SMALLINT)
    tid = Column(postgresql.BIGINT)
    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    nullable=False,
                    index=True,
                    primary_key=True)

class PerfEvent(BASE):
    """Store PAPI profiling based events."""

    __tablename__ = 'benchbuild_perf_events'

    name = Column(String, index=True)
    start = Column(postgresql.NUMERIC, primary_key=True)
    duration = Column(postgresql.NUMERIC)
    id = Column(Integer, primary_key=True)
    type = Column(postgresql.SMALLINT)
    tid = Column(postgresql.BIGINT)
    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    nullable=False,
                    index=True,
                    primary_key=True)

class Project(BASE):
    """Store project metadata."""

    __tablename__ = 'project'

    name = Column(String, primary_key=True)
    description = Column(String)
    src_url = Column(String)
    domain = Column(String)
    group_name = Column(String)
    version = Column(String)

    def __repr__(self):
        return "<Project {group}@{domain}/{name} V:{version}>".format(
            group=self.group_name,
            domain=self.domain,
            name=self.name,
            version=self.version)


class CompileStat(BASE):
    """Store compilestats as given by LLVM's '-stats' commoand."""

    __tablename__ = 'compilestats'

    id = Column(postgresql.BIGINT, primary_key=True)
    name = Column(String, index=True)
    component = Column(String, index=True)
    value = Column(postgresql.NUMERIC)
    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    index=True)


class RunLog(BASE):
    """
    Store log information for every run.

    Properties like, start time, finish time, exit code, stderr, stdout
    are stored here.
    """

    __tablename__ = 'log'

    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    index=True,
                    primary_key=True)
    begin = Column(DateTime(timezone=False))
    end = Column(DateTime(timezone=False))
    status = Column(Integer)
    config = Column(String)
    stderr = Column(String)
    stdout = Column(String)


class Metadata(BASE):
    """
    Store metadata information for every run.

    If you happen to have some free-form data that belongs to the database,
    this is the place for it.
    """

    __tablename__ = "metadata"

    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    index=True,
                    primary_key=True)
    name = Column(String)
    value = Column(String)


class Config(BASE):
    """
    Store customized information about a run.

    You can store arbitrary configuration information about a run here.
    Use it for extended filtering against the run table.
    """

    __tablename__ = 'config'

    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    index=True,
                    primary_key=True)
    name = Column(String, primary_key=True)
    value = Column(String)


class GlobalConfig(BASE):
    """
    Store customized information about a run.

    You can store arbitrary configuration information about a run here.
    Use it for extended filtering against the run table.
    """

    __tablename__ = 'globalconfig'

    experiment_group = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("experiment.id",
                   onupdate="CASCADE",
                   ondelete="CASCADE"),
        primary_key=True)
    name = Column(String, primary_key=True)
    value = Column(String)


class RegressionTest(BASE):
    """
    Store regression tests for all projects.

    This relation is filled from the PolyJIT side, not from benchbuild-study.
    We collect all JIT SCoPs found by PolyJIT in this relation for
    regression-test generation.

    """

    __tablename__ = 'regressions'
    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    index=True,
                    primary_key=True)
    name = Column(String)
    module = Column(String)
    project_name = Column(String)


class SessionManager(object):
    def __init__(self):
        logger = logging.getLogger(__name__)

        self.__test_mode = CFG['db']['rollback'].value()
        self.__engine = create_engine(
            "{dialect}://{u}:{p}@{h}:{P}/{db}".format(
                u=CFG["db"]["user"],
                h=CFG["db"]["host"],
                P=CFG["db"]["port"],
                p=CFG["db"]["pass"],
                db=CFG["db"]["name"],
                dialect=CFG["db"]["dialect"]))
        self.__connection = self.__engine.connect()
        self.__transaction = None
        if self.__test_mode:
            logger.warning(
                "DB test mode active, all actions will be rolled back.")
            self.__transaction = self.__connection.begin()
        BASE.metadata.create_all(self.__connection, checkfirst=True)

    def get(self):
        return sessionmaker(bind=self.__connection)

    def __del__(self):
        if hasattr(self, '__transaction') and self.__transaction:
            self.__transaction.rollback()


CONNECTION_MANAGER = SessionManager()
"""
 Import this session manager to create new database sessions as needes.
"""
Session = CONNECTION_MANAGER.get()

