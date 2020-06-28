import abc
import six
from abc import abstractmethod
from typing import Any, Optional

class ProgressBase(six.ABC, metaclass=abc.ABCMeta):
    length: Any = ...
    iterator: Any = ...
    timer: Any = ...
    body: Any = ...
    has_output: Any = ...
    clear: Any = ...
    def __init__(self, iterator: Optional[Any] = ..., length: Optional[Any] = ..., timer: bool = ..., body: bool = ..., has_output: bool = ..., clear: bool = ...) -> None: ...
    def __len__(self): ...
    def __iter__(self) -> Any: ...
    iter: Any = ...
    @abstractmethod
    def start(self) -> Any: ...
    def __next__(self): ...
    def next(self): ...
    @property
    def value(self): ...
    @value.setter
    def value(self, val: Any) -> None: ...
    @abstractmethod
    def display(self) -> Any: ...
    def increment(self) -> None: ...
    def time_remaining(self): ...
    def str_time_remaining(self): ...
    @abstractmethod
    def done(self) -> Any: ...
    @classmethod
    def range(cls, *value: Any, **kargs: Any): ...
    @classmethod
    def wrap(cls, iterator: Any, length: Optional[Any] = ..., **kargs: Any): ...

class Progress(ProgressBase):
    def start(self) -> None: ...
    value: Any = ...
    def done(self) -> None: ...
    def display(self) -> None: ...

class ProgressIPy(ProgressBase):
    HTMLBOX: str = ...
    prog: Any = ...
    def __init__(self, *args: Any, **kargs: Any) -> None: ...
    def start(self) -> None: ...
    @property
    def value(self): ...
    @value.setter
    def value(self, val: Any) -> None: ...
    def display(self) -> None: ...
    def done(self) -> None: ...

class ProgressAuto(ProgressBase, metaclass=abc.ABCMeta):
    def __new__(cls, *args: Any, **kargs: Any): ...

def main() -> None: ...
