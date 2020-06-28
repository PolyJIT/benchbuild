from migrate.versioning.config import *
from optparse import OptionParser
from typing import Any, Optional

alias: Any

def alias_setup() -> None: ...

class PassiveOptionParser(OptionParser): ...

def main(argv: Optional[Any] = ..., **kwargs: Any): ...
