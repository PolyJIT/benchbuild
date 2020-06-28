from sqlalchemy import create_engine as create_engine
from typing import Any, Optional

log: Any

class ControlledSchema:
    engine: Any = ...
    repository: Any = ...
    meta: Any = ...
    def __init__(self, engine: Any, repository: Any) -> None: ...
    def __eq__(self, other: Any) -> Any: ...
    table: Any = ...
    version: Any = ...
    def load(self): ...
    def drop(self) -> None: ...
    def changeset(self, version: Optional[Any] = ...): ...
    def runchange(self, ver: Any, change: Any, step: Any) -> None: ...
    def update_repository_table(self, startver: Any, endver: Any) -> None: ...
    def upgrade(self, version: Optional[Any] = ...) -> None: ...
    def update_db_from_model(self, model: Any) -> None: ...
    @classmethod
    def create(cls, engine: Any, repository: Any, version: Optional[Any] = ...): ...
    @classmethod
    def compare_model_to_db(cls, engine: Any, model: Any, repository: Any): ...
    @classmethod
    def create_model(cls, engine: Any, repository: Any, declarative: bool = ...): ...
