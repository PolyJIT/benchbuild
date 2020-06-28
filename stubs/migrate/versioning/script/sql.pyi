from migrate.versioning.script import base
from typing import Any, Optional

log: Any

class SqlScript(base.BaseScript):
    @classmethod
    def create(cls, path: Any, **opts: Any): ...
    def run(self, engine: Any, step: Optional[Any] = ...) -> None: ...
