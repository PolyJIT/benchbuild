from migrate.versioning import pathed
from typing import Any, Optional

log: Any

class VerNum:
    def __new__(cls, value: Any): ...
    value: Any = ...
    def __init__(self, value: Any) -> None: ...
    def __add__(self, value: Any): ...
    def __sub__(self, value: Any): ...
    def __eq__(self, value: Any) -> Any: ...
    def __ne__(self, value: Any) -> Any: ...
    def __lt__(self, value: Any) -> Any: ...
    def __gt__(self, value: Any) -> Any: ...
    def __ge__(self, value: Any) -> Any: ...
    def __le__(self, value: Any) -> Any: ...
    def __int__(self): ...
    def __index__(self): ...
    def __hash__(self) -> Any: ...

class Collection(pathed.Pathed):
    FILENAME_WITH_VERSION: Any = ...
    versions: Any = ...
    def __init__(self, path: Any) -> None: ...
    @property
    def latest(self): ...
    def create_new_python_version(self, description: Any, **k: Any) -> None: ...
    def create_new_sql_version(self, database: Any, description: Any, **k: Any) -> None: ...
    def version(self, vernum: Optional[Any] = ...): ...
    @classmethod
    def clear(cls) -> None: ...

class Version:
    version: Any = ...
    sql: Any = ...
    python: Any = ...
    def __init__(self, vernum: Any, path: Any, filelist: Any) -> None: ...
    def script(self, database: Optional[Any] = ..., operation: Optional[Any] = ...): ...
    def add_script(self, path: Any) -> None: ...
    SQL_FILENAME: Any = ...

class Extensions:
    py: str = ...
    sql: str = ...

def str_to_filename(s: Any): ...
