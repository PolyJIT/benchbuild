import pandas.core.common as pd
from pandas.core.computation import expr, ops, scope as _scope
from pandas.core.computation.expr import BaseExprVisitor
from typing import Any, Dict, Optional, Tuple

class PyTablesScope(_scope.Scope):
    queryables: Dict[str, Any]
    def __init__(self, level: int, global_dict: Any=..., local_dict: Any=..., queryables: Optional[Dict[str, Any]]=...) -> None: ...

class Term(ops.Term):
    env: PyTablesScope
    def __new__(cls, name: Any, env: Any, side: Optional[Any] = ..., encoding: Optional[Any] = ...): ...
    def __init__(self, name: Any, env: PyTablesScope, side: Any=..., encoding: Any=...) -> None: ...
    @property
    def value(self): ...

class Constant(Term):
    def __init__(self, value: Any, env: PyTablesScope, side: Any=..., encoding: Any=...) -> None: ...

class BinOp(ops.BinOp):
    op: str
    queryables: Dict[str, Any]
    encoding: Any = ...
    condition: Any = ...
    def __init__(self, op: str, lhs: Any, rhs: Any, queryables: Dict[str, Any], encoding: Any) -> None: ...
    def prune(self, klass: Any): ...
    def conform(self, rhs: Any): ...
    @property
    def is_valid(self) -> bool: ...
    @property
    def is_in_table(self) -> bool: ...
    @property
    def kind(self): ...
    @property
    def meta(self): ...
    @property
    def metadata(self): ...
    def generate(self, v: Any) -> str: ...
    def convert_value(self, v: Any) -> TermValue: ...
    def convert_values(self) -> None: ...

class FilterBinOp(BinOp):
    filter: Optional[Tuple[Any, Any, pd.Index]] = ...
    def invert(self): ...
    def format(self): ...
    def evaluate(self): ...
    def generate_filter_op(self, invert: bool=...) -> Any: ...

class JointFilterBinOp(FilterBinOp):
    def format(self) -> None: ...
    def evaluate(self): ...

class ConditionBinOp(BinOp):
    def invert(self) -> None: ...
    def format(self): ...
    condition: Any = ...
    def evaluate(self): ...

class JointConditionBinOp(ConditionBinOp):
    condition: Any = ...
    def evaluate(self): ...

class UnaryOp(ops.UnaryOp):
    def prune(self, klass: Any): ...

class PyTablesExprVisitor(BaseExprVisitor):
    const_type: Any = ...
    term_type: Any = ...
    def __init__(self, env: Any, engine: Any, parser: Any, **kwargs: Any): ...
    def visit_UnaryOp(self, node: Any, **kwargs: Any): ...
    def visit_Index(self, node: Any, **kwargs: Any): ...
    def visit_Assign(self, node: Any, **kwargs: Any): ...
    def visit_Subscript(self, node: Any, **kwargs: Any): ...
    def visit_Attribute(self, node: Any, **kwargs: Any): ...
    def translate_In(self, op: Any): ...

class PyTablesExpr(expr.Expr):
    env: PyTablesScope
    encoding: Any = ...
    condition: Any = ...
    filter: Any = ...
    terms: Any = ...
    expr: Any = ...
    def __init__(self, where: Any, queryables: Optional[Dict[str, Any]]=..., encoding: Any=..., scope_level: int=...) -> None: ...
    def evaluate(self): ...

class TermValue:
    value: Any = ...
    converted: Any = ...
    kind: Any = ...
    def __init__(self, value: Any, converted: Any, kind: str) -> None: ...
    def tostring(self, encoding: Any) -> str: ...

def maybe_expression(s: Any) -> bool: ...
