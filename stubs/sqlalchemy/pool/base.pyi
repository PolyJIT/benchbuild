from .. import log
from typing import Any, Optional

reset_rollback: Any
reset_commit: Any
reset_none: Any

class _ConnDialect:
    def do_rollback(self, dbapi_connection: Any) -> None: ...
    def do_commit(self, dbapi_connection: Any) -> None: ...
    def do_close(self, dbapi_connection: Any) -> None: ...
    def do_ping(self, dbapi_connection: Any) -> None: ...

class Pool(log.Identified):
    logging_name: Any = ...
    echo: Any = ...
    def __init__(self, creator: Any, recycle: int = ..., echo: Optional[Any] = ..., use_threadlocal: bool = ..., logging_name: Optional[Any] = ..., reset_on_return: bool = ..., listeners: Optional[Any] = ..., events: Optional[Any] = ..., dialect: Optional[Any] = ..., pre_ping: bool = ..., _dispatch: Optional[Any] = ...) -> None: ...
    def add_listener(self, listener: Any) -> None: ...
    def unique_connection(self): ...
    def recreate(self) -> None: ...
    def dispose(self) -> None: ...
    def connect(self): ...
    def status(self) -> None: ...

class _ConnectionRecord:
    finalize_callback: Any = ...
    def __init__(self, pool: Any, connect: bool = ...) -> None: ...
    fairy_ref: Any = ...
    starttime: Any = ...
    connection: Any = ...
    def info(self): ...
    def record_info(self): ...
    @classmethod
    def checkout(cls, pool: Any): ...
    def checkin(self, _no_fairy_ref: bool = ...) -> None: ...
    @property
    def in_use(self): ...
    @property
    def last_connect_time(self): ...
    def close(self) -> None: ...
    def invalidate(self, e: Optional[Any] = ..., soft: bool = ...) -> None: ...
    def get_connection(self): ...

class _ConnectionFairy:
    connection: Any = ...
    def __init__(self, dbapi_connection: Any, connection_record: Any, echo: Any) -> None: ...
    @property
    def is_valid(self): ...
    def info(self): ...
    @property
    def record_info(self): ...
    def invalidate(self, e: Optional[Any] = ..., soft: bool = ...) -> None: ...
    def cursor(self, *args: Any, **kwargs: Any): ...
    def __getattr__(self, key: Any): ...
    def detach(self) -> None: ...
    def close(self) -> None: ...
