"""Database schema for pprof."""

import logging
from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pprof.settings import CFG

CFG['db'] = {
    "host": {
        "desc": "host name of our db.",
        "default": "localhost"
    },
    "port": {
        "desc": "port to connect to the database",
        "default": 5432
    },
    "name": {
        "desc": "The name of the PostgreSQL database that will be used.",
        "default": "pprof"
    },
    "user": {
        "desc":
        "The name of the PostgreSQL user to connect to the database with.",
        "default": "pprof"
    },
    "pass": {
        "desc":
        "The password for the PostgreSQL user used to connect to the database with.",
        "default": "pprof"
    },
    "rollback": {
        "desc": "Rollback all operations after pprof completes.",
        "default": False
    }
}

Base = declarative_base()


class Run(Base):
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


class RunGroup(Base):
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


class Experiment(Base):
    """Store metadata about experiments."""

    __tablename__ = 'experiment'

    name = Column(String)
    description = Column(String)
    id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    begin = Column(DateTime(timezone=False))
    end = Column(DateTime(timezone=False))

    def __repr__(self):
        return "<Experiment {name}>".format(name=self.name)


class Likwid(Base):
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


class Metric(Base):
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
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    nullable=False,
                    index=True,
                    primary_key=True)


class Project(Base):
    """Store project metadata."""

    __tablename__ = 'project'

    name = Column(String, primary_key=True)
    description = Column(String)
    src_url = Column(String)
    domain = Column(String)
    group_name = Column(String)

    def __repr__(self):
        return "<Project {group}@{domain}/{name}>".format(
            group=self.group_name,
            domain=self.domain,
            name=self.name)


class CompileStat(Base):
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


class RunLog(Base):
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


class Metadata(Base):
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


class Config(Base):
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


class GlobalConfig(Base):
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


class RegressionTest(Base):
    """
    Store regression tests for all projects.

    This relation is filled from the PolyJIT side, not from pprof-study.
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
            "postgresql+psycopg2://{u}:{p}@{h}:{P}/{db}".format(
                u=CFG["db"]["user"],
                h=CFG["db"]["host"],
                P=CFG["db"]["port"],
                p=CFG["db"]["pass"],
                db=CFG["db"]["name"]))
        self.__connection = self.__engine.connect()
        if self.__test_mode:
            logger.warning(
                "DB test mode active, all actions will be rolled back.")
            self.__transaction = self.__connection.begin()
        Base.metadata.create_all(self.__connection, checkfirst=True)

    def get(self):
        return sessionmaker(bind=self.__connection)

    def __del__(self):
        if self.__test_mode:
            self.__transaction.rollback()


CONNECTION_MANAGER = SessionManager()
"""
 Import this session manager to create new database sessions as needes.
"""
Session = CONNECTION_MANAGER.get()
