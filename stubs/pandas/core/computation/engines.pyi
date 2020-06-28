import abc
from typing import Any

class NumExprClobberingError(NameError): ...

class AbstractEngine(metaclass=abc.ABCMeta):
    has_neg_frac: bool = ...
    expr: Any = ...
    aligned_axes: Any = ...
    result_type: Any = ...
    def __init__(self, expr: Any) -> None: ...
    def convert(self) -> str: ...
    def evaluate(self) -> object: ...

class NumExprEngine(AbstractEngine):
    has_neg_frac: bool = ...

class PythonEngine(AbstractEngine):
    has_neg_frac: bool = ...
    def evaluate(self): ...
