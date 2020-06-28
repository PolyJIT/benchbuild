from ...sql import expression
from ...types import TypeDecorator
from typing import Any

ischema: Any

class CoerceUnicode(TypeDecorator):
    impl: Any = ...
    def process_bind_param(self, value: Any, dialect: Any): ...
    def bind_expression(self, bindvalue: Any): ...

class _cast_on_2005(expression.ColumnElement):
    bindvalue: Any = ...
    def __init__(self, bindvalue: Any) -> None: ...

schemata: Any
tables: Any
columns: Any
constraints: Any
column_constraints: Any
key_constraints: Any
ref_constraints: Any
views: Any
computed_columns: Any
