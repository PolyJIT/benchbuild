from plumbum.path.base import Path
from typing import Any, Optional

logger: Any

class LocalPath(Path):
    CASE_SENSITIVE: Any = ...
    def __new__(cls, *parts: Any): ...
    def __fspath__(self): ...
    @property
    def name(self): ...
    @property
    def dirname(self): ...
    @property
    def suffix(self): ...
    @property
    def suffixes(self): ...
    @property
    def uid(self): ...
    @property
    def gid(self): ...
    def join(self, *others: Any): ...
    def list(self): ...
    def iterdir(self): ...
    def is_dir(self): ...
    def is_file(self): ...
    def is_symlink(self): ...
    def exists(self): ...
    def stat(self): ...
    def with_name(self, name: Any): ...
    @property
    def stem(self): ...
    def with_suffix(self, suffix: Any, depth: int = ...): ...
    def glob(self, pattern: Any): ...
    def delete(self) -> None: ...
    def move(self, dst: Any): ...
    def copy(self, dst: Any, override: Optional[Any] = ...): ...
    def mkdir(self, mode: int = ..., parents: bool = ..., exist_ok: bool = ...) -> None: ...
    def open(self, mode: str = ...): ...
    def read(self, encoding: Optional[Any] = ..., mode: str = ...): ...
    def write(self, data: Any, encoding: Optional[Any] = ..., mode: Optional[Any] = ...) -> None: ...
    def touch(self) -> None: ...
    def chown(self, owner: Optional[Any] = ..., group: Optional[Any] = ..., recursive: Optional[Any] = ...) -> None: ...
    def chmod(self, mode: Any) -> None: ...
    def access(self, mode: int = ...): ...
    def link(self, dst: Any) -> None: ...
    def symlink(self, dst: Any) -> None: ...
    def unlink(self) -> None: ...
    def as_uri(self, scheme: str = ...): ...
    @property
    def drive(self): ...
    @property
    def root(self): ...

class LocalWorkdir(LocalPath):
    def __hash__(self) -> Any: ...
    def __new__(cls): ...
    def chdir(self, newdir: Any): ...
    def getpath(self): ...
    def __call__(self, newdir: Any) -> None: ...
