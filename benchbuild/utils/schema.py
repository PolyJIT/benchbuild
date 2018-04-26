"""
# Database schema for benchbuild

The schema should initialize itself on an empty database. For now, we do not
support automatic upgrades on schema changes. You might encounter some
roadbumps when using an older version of benchbuild.

Furthermore, for now, we are restricted to postgresql databases, although we
already support arbitrary connection strings via config.

If you want to use reports that use one of our SQL functions, you need to
initialize the functions first using the following command:

```bash
  > BB_DB_CREATE_FUNCTIONS=true benchbuild run -E empty -l
```

After that you (normally) do not need to do this agains, unless we supply
a new version that you are interested in.
As soon as we have alembic running, we can provide automatic up/downgrade
paths for you.
"""

import logging
import uuid

import migrate.versioning.api as migrate
import sqlalchemy as sa
from sqlalchemy import (Column, DateTime, Enum, ForeignKey,
                        ForeignKeyConstraint, Integer, String, create_engine)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import (CHAR, BigInteger, Float, Numeric, SmallInteger,
                              TypeDecorator)

import benchbuild.settings as settings
import benchbuild.utils.user_interface as ui
from benchbuild.utils import path as bbpath

BASE = declarative_base()
LOG = logging.getLogger(__name__)


def metadata():
    return BASE.metadata


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
                return "%s" % uuid.UUID(value)
            else:
                # hexstring
                return "%x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        if isinstance(value, uuid.UUID):
            return value
        else:
            LOG.error(str(value))
            return uuid.UUID(str(value))


class Run(BASE):
    """Store a run for each executed test binary."""

    __tablename__ = 'run'
    __table_args__ = (ForeignKeyConstraint(
        ['project_name', 'project_group'],
        ['project.name', 'project.group_name']), )

    id = Column(Integer, primary_key=True)
    command = Column(String)
    project_name = Column(String, index=True)
    project_group = Column(String, index=True)
    experiment_name = Column(String, index=True)
    run_group = Column(GUID(as_uuid=True), index=True)
    experiment_group = Column(
        GUID(as_uuid=True), ForeignKey("experiment.id"), index=True)
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
    experiment = Column(
        GUID(as_uuid=True),
        ForeignKey("experiment.id", ondelete="CASCADE", onupdate="CASCADE"),
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


class Project(BASE):
    """Store project metadata."""

    __tablename__ = 'project'

    name = Column(String, primary_key=True)
    description = Column(String)
    src_url = Column(String)
    domain = Column(String)
    group_name = Column(String, primary_key=True)
    version = Column(String)

    def __repr__(self):
        return "<Project {group}@{domain}/{name} V:{version}>".format(
            group=self.group_name,
            domain=self.domain,
            name=self.name,
            version=self.version)


class Metric(BASE):
    """Store default metrics, simple name value store."""

    __tablename__ = 'metrics'

    name = Column(String, primary_key=True, index=True, nullable=False)
    value = Column(Float)
    run_id = Column(
        Integer,
        ForeignKey("run.id", onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
        primary_key=True)

    def __repr__(self):
        return "{0} - {1}".format(self.name, self.value)


class Event(BASE):
    """Store PAPI profiling based events."""

    __tablename__ = 'benchbuild_events'

    name = Column(String, index=True)
    start = Column(Numeric, primary_key=True)
    duration = Column(Numeric)
    id = Column(Integer, primary_key=True)
    type = Column(SmallInteger)
    tid = Column(BigInteger)
    run_id = Column(
        Integer,
        ForeignKey("run.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
        primary_key=True)


class RunLog(BASE):
    """
    Store log information for every run.

    Properties like, start time, finish time, exit code, stderr, stdout
    are stored here.
    """

    __tablename__ = 'log'

    run_id = Column(
        Integer,
        ForeignKey("run.id", onupdate="CASCADE", ondelete="CASCADE"),
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

    run_id = Column(
        Integer,
        ForeignKey("run.id", onupdate="CASCADE", ondelete="CASCADE"),
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

    run_id = Column(
        Integer,
        ForeignKey("run.id", onupdate="CASCADE", ondelete="CASCADE"),
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
        ForeignKey("experiment.id", onupdate="CASCADE", ondelete="CASCADE"),
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
    run_id = Column(
        Integer,
        ForeignKey("run.id", onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
        primary_key=True)
    name = Column(String)
    module = Column(String)
    project_name = Column(String)


def needed_schema(connection, meta):
    try:
        meta.create_all(connection, checkfirst=False)
    except sa.exc.ProgrammingError:
        return False
    return True


def setup_versioning():
    connect_str = settings.CFG["db"]["connect_string"].value()
    repo_url = bbpath.template_path("../db/")

    repo_version = migrate.version(repo_url, url=connect_str)
    db_version = None
    requires_versioning = False
    try:
        db_version = migrate.db_version(connect_str, repo_url)
    except migrate.exceptions.DatabaseNotControlledError:
        requires_versioning = True

    if requires_versioning:
        LOG.warning("Your database uses an unversioned benchbuild schema.")
        if not ui.ask("Should I enforce version control on your schema?"):
            LOG.error("User declined schema versioning.")
        migrate.version_control(connect_str, repo_url)
        return setup_versioning()

    return (repo_version, db_version)


def maybe_update_db(repo_version, db_version):
    if db_version is None:
        db_version = -1
    if db_version == repo_version:
        return

    LOG.warning("Your database contains version '%s' of benchbuild's schema.",
                db_version)
    LOG.warning(
        "Benchbuild currently requires version '%s' to work correctly.",
        repo_version)
    if not ui.ask("Should I attempt to update your schema to version '{0}'?".
                  format(repo_version)):
        LOG.error("User declined schema upgrade.")

    connect_str = settings.CFG["db"]["connect_string"].value()
    repo_url = bbpath.template_path("../db/")
    LOG.info("Upgrading to newest version...")
    migrate.upgrade(connect_str, repo_url)
    LOG.info("Complete.")


class SessionManager(object):
    def __init__(self):
        self.__test_mode = settings.CFG['db']['rollback'].value()
        self.engine = create_engine(
            settings.CFG["db"]["connect_string"].value())
        self.connection = self.engine.connect()
        try:
            self.connection.execution_options(isolation_level="READ COMMITTED")
        except sa.exc.ArgumentError:
            LOG.error("Unable to set isolation level to READ COMMITTED")

        self.__transaction = None
        if self.__test_mode:
            LOG.warning(
                "DB test mode active, all actions will be rolled back.")
            self.__transaction = self.connection.begin()

        if needed_schema(self.connection, BASE.metadata):
            LOG.debug("Initialized new db schema.")
        repo_version, db_version = setup_versioning()
        maybe_update_db(repo_version, db_version)

    def get(self):
        return sessionmaker(bind=self.connection)

    def __del__(self):
        if hasattr(self, '__transaction') and self.__transaction:
            self.__transaction.rollback()


def __lazy_session__():
    """Initialize the connection manager lazily."""
    connection_manager = None
    session = None

    def __lazy_session_wrapped():
        nonlocal connection_manager
        nonlocal session
        if connection_manager is None:
            connection_manager = SessionManager()
        if session is None:
            session = connection_manager.get()()
        return session

    return __lazy_session_wrapped


Session = __lazy_session__()


def init_functions(connection):
    """Initialize all SQL functions in the database."""
    if settings.CFG["db"]["create_functions"].value():
        print("Refreshing SQL functions...")
        for file in bbpath.template_files("../sql/", exts=[".sql"]):
            func = sa.DDL(bbpath.template_str(file))
            LOG.info("Loading: '%s' into database", file)
            connection.execute(func)
            connection.commit()
