from collections import namedtuple
from functools import lru_cache as lru_cache
from shutil import get_terminal_size as get_terminal_size, which as which
from typing import Any

PY3: Any
long = int
xrange = range
unicode = str
basestring = str

def u(s: Any): ...
def b(s: Any): ...
FileNotFoundError = FileNotFoundError
PermissionError = PermissionError
ProcessLookupError = ProcessLookupError
InterruptedError = InterruptedError
ChildProcessError = ChildProcessError
FileExistsError = FileExistsError

_CacheInfo = namedtuple('CacheInfo', ['hits', 'misses', 'maxsize', 'currsize'])

class _HashedSeq(list):
    hashvalue: Any = ...
    def __init__(self, tup: Any, hash: Any = ...) -> None: ...
    def __hash__(self) -> Any: ...
