from migrate.versioning.config import *
from migrate.versioning import pathed
from six.moves.configparser import ConfigParser
from typing import Any, Optional

class Parser(ConfigParser):
    def to_dict(self, sections: Optional[Any] = ...): ...

class Config(pathed.Pathed, Parser):
    def __init__(self, path: Any, *p: Any, **k: Any) -> None: ...
