from typing import Any, Optional

def pid_exists(pid: Any): ...
def wait_pid(pid: Any, timeout: Optional[Any] = ..., proc_name: Optional[Any] = ...): ...
def disk_usage(path: Any): ...
def get_terminal_map(): ...
