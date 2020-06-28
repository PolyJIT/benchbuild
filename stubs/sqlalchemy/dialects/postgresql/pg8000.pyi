from ... import types as sqltypes
from .base import PGCompiler, PGDialect, PGExecutionContext, PGIdentifierPreparer, UUID
from .json import JSON
from typing import Any, Optional

class _PGNumeric(sqltypes.Numeric):
    def result_processor(self, dialect: Any, coltype: Any): ...

class _PGNumericNoBind(_PGNumeric):
    def bind_processor(self, dialect: Any) -> None: ...

class _PGJSON(JSON):
    def result_processor(self, dialect: Any, coltype: Any): ...

class _PGUUID(UUID):
    def bind_processor(self, dialect: Any): ...
    def result_processor(self, dialect: Any, coltype: Any): ...

class PGExecutionContext_pg8000(PGExecutionContext): ...

class PGCompiler_pg8000(PGCompiler):
    def visit_mod_binary(self, binary: Any, operator: Any, **kw: Any): ...
    def post_process_text(self, text: Any): ...

class PGIdentifierPreparer_pg8000(PGIdentifierPreparer): ...

class PGDialect_pg8000(PGDialect):
    driver: str = ...
    supports_unicode_statements: bool = ...
    supports_unicode_binds: bool = ...
    default_paramstyle: str = ...
    supports_sane_multi_rowcount: bool = ...
    execution_ctx_cls: Any = ...
    statement_compiler: Any = ...
    preparer: Any = ...
    description_encoding: str = ...
    colspecs: Any = ...
    client_encoding: Any = ...
    def __init__(self, client_encoding: Optional[Any] = ..., **kwargs: Any) -> None: ...
    def initialize(self, connection: Any) -> None: ...
    @classmethod
    def dbapi(cls): ...
    def create_connect_args(self, url: Any): ...
    def is_disconnect(self, e: Any, connection: Any, cursor: Any): ...
    def set_isolation_level(self, connection: Any, level: Any) -> None: ...
    def set_client_encoding(self, connection: Any, client_encoding: Any) -> None: ...
    def do_begin_twophase(self, connection: Any, xid: Any) -> None: ...
    def do_prepare_twophase(self, connection: Any, xid: Any) -> None: ...
    def do_rollback_twophase(self, connection: Any, xid: Any, is_prepared: bool = ..., recover: bool = ...) -> None: ...
    def do_commit_twophase(self, connection: Any, xid: Any, is_prepared: bool = ..., recover: bool = ...) -> None: ...
    def do_recover_twophase(self, connection: Any): ...
    def on_connect(self): ...
dialect = PGDialect_pg8000
