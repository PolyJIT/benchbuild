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

After that you (normally)  do not need to do this agains, unless we supply
a new version that you are interested in.
As soon as we have alembic running, we can provide automatic up/downgrade
paths for you.
"""

import functools
import logging
import sys
import typing as tp
import uuid

import sqlalchemy as sa
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import CHAR, Float, TypeDecorator

from benchbuild import settings
from benchbuild.utils import path
from benchbuild.utils import user_interface as ui

BASE = declarative_base()
LOG = logging.getLogger(__name__)


def metadata():
    return BASE.metadata


def exceptions(
    error_is_fatal: bool = True,
    error_messages: tp.Optional[tp.Dict[Exception, str]] = None
) -> tp.Callable:
    """
    Handle SQLAlchemy exceptions in a sane way.

    Args:
        func: An arbitrary function to wrap.
        error_is_fatal: Should we exit the program on exception?
        reraise: Should we reraise the exception, after logging?
            Only makes sense if error_is_fatal is False.
        error_messages: A dictionary that assigns an exception class to a
            customized error message.
    """

    def exception_decorator(func):
        nonlocal error_messages

        @functools.wraps(func)
        def exc_wrapper(*args, **kwargs):
            nonlocal error_messages
            try:
                result = func(*args, **kwargs)
            except sa.exc.SQLAlchemyError as err:
                result = None
                details = None
                err_type = err.__class__
                if error_messages and err_type in error_messages:
                    details = error_messages[err_type]
                if details:
                    LOG.error(details)
                LOG.error("For developers: (%s) %s", err.__class__, str(err))
                if error_is_fatal:
                    sys.exit("Abort, SQL operation failed.")
                if not ui.ask(
                    "I can continue at your own risk, do you want that?"
                ):
                    raise err
            return result

        return exc_wrapper

    return exception_decorator


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR
    as_uuid = False
    cache_ok = False

    def __init__(self, *args, as_uuid=False, **kwargs):
        self.as_uuid = as_uuid
        super().__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID(as_uuid=self.as_uuid))
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        if isinstance(value, uuid.UUID):
            return value

        return uuid.UUID(str(value))


class Run(BASE):
    """Store a run for each executed test binary."""

    __tablename__ = 'run'
    __table_args__ = (
        ForeignKeyConstraint(['project_name', 'project_group'],
                             ['project.name', 'project.group_name'],
                             onupdate="CASCADE",
                             ondelete="CASCADE"),
    )

    id = Column(Integer, primary_key=True)
    command = Column(String)
    project_name = Column(String, index=True)
    project_group = Column(String, index=True)
    experiment_name = Column(String, index=True)
    run_group = Column(GUID(as_uuid=True), index=True)
    experiment_group = Column(
        GUID(as_uuid=True),
        ForeignKey("experiment.id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True
    )

    begin = Column(DateTime(timezone=False))
    end = Column(DateTime(timezone=False))
    status = Column(Enum('completed', 'running', 'failed', name="run_state"))

    metrics = sa.orm.relationship(
        "Metric",
        cascade="all, delete-orphan",
        passive_deletes=True,
        passive_updates=True
    )
    logs = sa.orm.relationship(
        "RunLog",
        cascade="all, delete-orphan",
        passive_deletes=True,
        passive_updates=True
    )
    stored_data = sa.orm.relationship(
        "Metadata",
        cascade="all, delete-orphan",
        passive_deletes=True,
        passive_updates=True
    )
    configurations = sa.orm.relationship(
        "Config",
        cascade="all, delete-orphan",
        passive_deletes=True,
        passive_updates=True
    )

    def __repr__(self):
        return ("<Run: {0} status={1} run={2}>"
               ).format(self.project_name, self.status, self.id)


class RunGroup(BASE):
    """ Store information about a run group. """

    __tablename__ = 'rungroup'

    id = Column(GUID(as_uuid=True), primary_key=True, index=True)
    experiment = Column(
        GUID(as_uuid=True),
        ForeignKey("experiment.id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True
    )

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

    runs = sa.orm.relationship(
        "Run",
        cascade="all, delete-orphan",
        passive_deletes=True,
        passive_updates=True
    )
    run_groups = sa.orm.relationship(
        "RunGroup",
        cascade="all, delete-orphan",
        passive_deletes=True,
        passive_updates=True
    )

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

    runs = sa.orm.relationship(
        "Run",
        cascade="all, delete-orphan",
        passive_deletes=True,
        passive_updates=True
    )

    def __repr__(self):
        return "<Project {group}@{domain}/{name} V:{version}>".format(
            group=self.group_name,
            domain=self.domain,
            name=self.name,
            version=self.version
        )


class Metric(BASE):
    """Store default metrics, simple name value store."""

    __tablename__ = 'metrics'

    name = Column(String, primary_key=True, index=True, nullable=False)
    value = Column(Float)
    run_id = Column(
        Integer,
        ForeignKey("run.id", onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
        primary_key=True
    )

    def __repr__(self):
        return "{0} - {1}".format(self.name, self.value)


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
        primary_key=True
    )
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
        primary_key=True
    )
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
        primary_key=True
    )
    name = Column(String, primary_key=True)
    value = Column(String)


def needed_schema(connection, meta):
    try:
        meta.create_all(connection, checkfirst=False)
    except sa.exc.CompileError as cerr:
        LOG.critical("Schema could not be created! Details: %s", str(cerr))
        sys.exit(-4)
    except sa.exc.OperationalError:
        # SQLite throws an OperationalError

        # Now try again to add user-defined tables unconditionally.
        meta.create_all(connection, checkfirst=True)
        return False
    except sa.exc.ProgrammingError:
        # PostgreSQL throws a ProgrammingError

        # Now try again to add user-defined tables unconditionally.
        meta.create_all(connection, checkfirst=True)
        return False
    return True


class SessionManager:

    def connect_engine(self):
        """
        Establish a connection to the database.

        Provides simple error handling for fatal errors.

        Returns:
            True, if we could establish a connection, else False.
        """
        try:
            self.connection = self.engine.connect()
            return True
        except sa.exc.OperationalError as opex:
            LOG.critical(
                "Could not connect to the database. The error was: '%s'",
                str(opex)
            )
        return False

    def configure_engine(self):
        """
        Configure the databse connection.

        Sets appropriate transaction isolation levels and handle errors.

        Returns:
            True, if we did not encounter any unrecoverable errors, else False.
        """
        try:
            self.connection.execution_options(isolation_level="SERIALIZABLE")
        except sa.exc.ArgumentError:
            LOG.debug("Unable to set isolation level to SERIALIZABLE")
        return True

    @exceptions(
        error_messages={
            sa.exc.NoSuchModuleError:
                "Connect string contained an invalid backend."
        }
    )
    def __init__(self):
        self.__test_mode = bool(settings.CFG['db']['rollback'])
        self.engine = create_engine(str(settings.CFG["db"]["connect_string"]))

        if not (self.connect_engine() and self.configure_engine()):
            sys.exit(-3)

        self.__transaction = None
        if self.__test_mode:
            LOG.warning("DB test mode active, all actions will be rolled back.")
            self.__transaction = self.connection.begin()

        if needed_schema(self.connection, BASE.metadata):
            LOG.debug("Initialized new db schema.")

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
    if settings.CFG["db"]["create_functions"]:
        print("Refreshing SQL functions...")
        for file in path.template_files("sql/", exts=[".sql"]):
            func = sa.DDL(path.template_str(file))
            LOG.info("Loading: '%s' into database", file)
            connection.execute(func)
            connection.commit()
