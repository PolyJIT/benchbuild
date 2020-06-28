from collections import namedtuple
from typing import Any, Optional

__extra__all__: Any
PAGE_SIZE: Any
AF_LINK: Any
IS_64_BIT: Any
CONN_IDLE: str
CONN_BOUND: str
PROC_STATUSES: Any
TCP_STATUSES: Any
proc_info_map: Any

scputimes = namedtuple('scputimes', ['user', 'system', 'idle', 'iowait'])

pcputimes = namedtuple('pcputimes', ['user', 'system', 'children_user', 'children_system'])

svmem = namedtuple('svmem', ['total', 'available', 'percent', 'used', 'free'])

pmem = namedtuple('pmem', ['rss', 'vms'])
pfullmem = pmem

pmmap_grouped = namedtuple('pmmap_grouped', ['path', 'rss', 'anonymous', 'locked'])

pmmap_ext: Any
def virtual_memory(): ...
def swap_memory(): ...
def cpu_times(): ...
def per_cpu_times(): ...
def cpu_count_logical(): ...
def cpu_count_physical(): ...
def cpu_stats(): ...

disk_io_counters: Any
disk_usage: Any

def disk_partitions(all: bool = ...): ...

net_io_counters: Any
net_if_addrs: Any

def net_connections(kind: Any, _pid: int = ...): ...
def net_if_stats(): ...
def boot_time(): ...
def users(): ...
def pids(): ...
def pid_exists(pid: Any): ...
def wrap_exceptions(fun: Any): ...

class Process:
    pid: Any = ...
    def __init__(self, pid: Any) -> None: ...
    def oneshot_enter(self) -> None: ...
    def oneshot_exit(self) -> None: ...
    def name(self): ...
    def exe(self): ...
    def cmdline(self): ...
    def environ(self): ...
    def create_time(self): ...
    def num_threads(self): ...
    def nice_get(self): ...
    def nice_set(self, value: Any): ...
    def ppid(self): ...
    def uids(self): ...
    def gids(self): ...
    def cpu_times(self): ...
    def cpu_num(self): ...
    def terminal(self): ...
    def cwd(self): ...
    def memory_info(self): ...
    memory_full_info: Any = ...
    def status(self): ...
    def threads(self): ...
    def open_files(self): ...
    def connections(self, kind: str = ...): ...

    nt_mmap_grouped = namedtuple('mmap', 'path rss anon locked')

    nt_mmap_ext = namedtuple('mmap', 'addr perms path rss anon locked')
    def memory_maps(self): ...
    def num_fds(self): ...
    def num_ctx_switches(self): ...
    def wait(self, timeout: Optional[Any] = ...): ...
