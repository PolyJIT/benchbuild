"""
Database schema for benchbuild
==============================

The schema should initialize itself on an empty database. For now, we do not
support automatic upgrades on schema changes. You might encounter some
roadbumps when using an older version of benchbuild.

Furthermore, for now, we are restricted to postgresql databases, although we
already support arbitrary connection strings via config.

If you want to use reports that use one of our SQL functions, you need to
initialize the functions first using the following command:

.. code-block:: bash

  > BB_DB_CREATE_FUNCTIONS=true benchbuild run -E empty -l

After that you (normally) do not need to do this agains, unless we supply
a new version that you are interested in.
As soon as we have alembic running, we can provide automatic up/downgrade
paths for you.
"""

import logging
import uuid
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from benchbuild.settings import CFG
from benchbuild.utils import path as bbpath

BASE = declarative_base()


"""Source: http://docs.sqlalchemy.org/en/rel_0_9/core/custom_types.html?highlight=guid#backend-agnostic-guid-type"""
class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR
    as_uuid = False

    def __init__(self, *args, as_uuid=False, **kwargs):
        self.as_uuid = as_uuid
        super(GUID, self).__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID(as_uuid=self.as_uuid))
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).bytes
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        if isinstance(value, uuid.UUID):
            return value
        else:
            return uuid.UUID(value)

"""Source: http://docs.sqlalchemy.org/en/rel_0_9/core/custom_types.html?highlight=guid#backend-agnostic-guid-type"""

class Run(BASE):
    """Store a run for each executed test binary."""

    __tablename__ = 'run'

    id = Column(Integer, primary_key=True)
    command = Column(String)
    project_name = Column(String, ForeignKey("project.name"), index=True)
    experiment_name = Column(String, index=True)
    run_group = Column(GUID(as_uuid=True), index=True)
    experiment_group = Column(GUID(as_uuid=True),
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

    id = Column(GUID(as_uuid=True), primary_key=True, index=True)
    project = Column(String, ForeignKey("project.name"), index=True)
    experiment = Column(
        GUID(as_uuid=True),
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
    id = Column(GUID(as_uuid=True), primary_key=True)
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


class Sequence(BASE):
    """Store a the fittest sequence of an opt command and its fitness value."""

    __tablename__ = 'sequences'

    #the sequence that offers the best fitness value
    name = Column(String, primary_key=False, index=True, nullable=False)

    #the fitness value of the sequence
    value = Column(postgresql.DOUBLE_PRECISION)

    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    index=True,
                    primary_key=True)


class Schedule(BASE):
    """Store default metrics, simple name value store."""

    __tablename__ = 'schedules'

    function = Column(String, primary_key=True, index=True, nullable=False)
    schedule = Column(String, primary_key=True, index=True, nullable=False)
    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    index=True,
                    primary_key=True)


class IslAst(BASE):
    """Store default metrics, simple name value store."""

    __tablename__ = 'isl_asts'

    function = Column(String, primary_key=True, index=True, nullable=False)
    ast = Column(String, primary_key=True, index=True, nullable=False)
    run_id = Column(Integer,
                    ForeignKey("run.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    index=True,
                    primary_key=True)


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
        GUID(as_uuid=True),
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
        self.engine = create_engine(
            "{dialect}://{u}:{p}@{h}:{P}/{db}".format(
                u=CFG["db"]["user"],
                h=CFG["db"]["host"],
                P=CFG["db"]["port"],
                p=CFG["db"]["pass"],
                db=CFG["db"]["name"],
                dialect=CFG["db"]["dialect"]))
        self.connection = self.engine.connect()
        self.__transaction = None
        if self.__test_mode:
            logger.warning(
                "DB test mode active, all actions will be rolled back.")
            self.__transaction = self.connection.begin()

        BASE.metadata.create_all(self.connection, checkfirst=True)

    def get(self):
        return sessionmaker(bind=self.connection)

    def __del__(self):
        if hasattr(self, '__transaction') and self.__transaction:
            self.__transaction.rollback()


def __lazy_session__():
    """Initialize the connection manager lazily."""
    connection_manager = None

    def __lazy_session_wrapped():
        nonlocal connection_manager
        if connection_manager is None:
            connection_manager = SessionManager()
        return connection_manager.get()()

    return __lazy_session_wrapped

Session = __lazy_session__()


def init_functions(connection):
    """Initialize all SQL functions in the database."""
    if CFG["db"]["create_functions"].value():
        print("Refreshing SQL functions...")
    for file in bbpath.template_files("../sql/", exts=[".sql"]):
        func = sa.DDL(
            bbpath.template_str(file)
        )
        print("Loading: {0}".format(file))
        print(func.compile())
        connection.execute(func)
        connection.commit()

