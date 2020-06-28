from typing import Any

log: Any
HEADER: str
META_DEFINITION: str
DECLARATIVE_DEFINITION: str

class ModelGenerator:
    diff: Any = ...
    engine: Any = ...
    declarative: Any = ...
    def __init__(self, diff: Any, engine: Any, declarative: bool = ...) -> None: ...
    def column_repr(self, col: Any): ...
    def genBDefinition(self): ...
    def genB2AMigration(self, indent: str = ...): ...
    def runB2A(self): ...
