from .mysqldb import MySQLDialect_mysqldb
from typing import Any

class MySQLDialect_gaerdbms(MySQLDialect_mysqldb):
    @classmethod
    def dbapi(cls): ...
    @classmethod
    def get_pool_class(cls, url: Any): ...
    def create_connect_args(self, url: Any): ...
dialect = MySQLDialect_gaerdbms
