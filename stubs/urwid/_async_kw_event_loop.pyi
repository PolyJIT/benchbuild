from .main_loop import EventLoop
from typing import Any, Optional

class TrioEventLoop(EventLoop):
    def __init__(self, nursery: Optional[Any] = ...) -> None: ...
    def alarm(self, seconds: Any, callback: Any): ...
    def enter_idle(self, callback: Any): ...
    def remove_alarm(self, handle: Any): ...
    def remove_enter_idle(self, handle: Any): ...
    def remove_watch_file(self, handle: Any): ...
    def run(self): ...
    def watch_file(self, fd: Any, callback: Any): ...
