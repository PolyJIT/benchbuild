from sqlalchemy import types as sqltypes
from sqlalchemy.connectors.pyodbc import PyODBCConnector
from sqlalchemy.dialects.sybase.base import SybaseDialect, SybaseExecutionContext
from typing import Any

class _SybNumeric_pyodbc(sqltypes.Numeric):
    def bind_processor(self, dialect: Any): ...

class SybaseExecutionContext_pyodbc(SybaseExecutionContext):
    def set_ddl_autocommit(self, connection: Any, value: Any) -> None: ...

class SybaseDialect_pyodbc(PyODBCConnector, SybaseDialect):
    execution_ctx_cls: Any = ...
    colspecs: Any = ...
dialect = SybaseDialect_pyodbc
