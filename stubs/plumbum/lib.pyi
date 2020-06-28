from typing import Any, Optional

IS_WIN32: Any

class ProcInfo:
    pid: Any = ...
    uid: Any = ...
    stat: Any = ...
    args: Any = ...
    def __init__(self, pid: Any, uid: Any, stat: Any, args: Any) -> None: ...

class six:
    PY3: Any = ...
    getfullargspec: Any = ...
    integer_types: Any = ...
    string_types: Any = ...
    MAXSIZE: Any = ...
    ascii: Any = ...
    bytes: Any = ...
    unicode_type: Any = ...
    @staticmethod
    def b(s: Any): ...
    @staticmethod
    def u(s: Any): ...
    @staticmethod
    def get_method_function(m: Any): ...
    str: Any = ...

def captured_stdout(stdin: str = ...) -> None: ...

class StaticProperty:
    __doc__: Any = ...
    def __init__(self, function: Any) -> None: ...
    def __get__(self, obj: Any, klass: Optional[Any] = ...): ...

def getdoc(object: Any): ...
def read_fd_decode_safely(fd: Any, size: int = ...): ...
