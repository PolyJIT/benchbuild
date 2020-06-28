from .base import BIT
from .mysqldb import MySQLDialect_mysqldb
from typing import Any

class _cymysqlBIT(BIT):
    def result_processor(self, dialect: Any, coltype: Any): ...

class MySQLDialect_cymysql(MySQLDialect_mysqldb):
    driver: str = ...
    description_encoding: Any = ...
    supports_sane_rowcount: bool = ...
    supports_sane_multi_rowcount: bool = ...
    supports_unicode_statements: bool = ...
    colspecs: Any = ...
    @classmethod
    def dbapi(cls): ...
    def is_disconnect(self, e: Any, connection: Any, cursor: Any): ...
dialect = MySQLDialect_cymysql
