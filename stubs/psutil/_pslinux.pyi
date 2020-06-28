import enum
from collections import namedtuple
from typing import Any, Optional

__extra__all__: Any
POWER_SUPPLY_PATH: str
HAS_SMAPS: Any
HAS_PRLIMIT: Any
HAS_PROC_IO_PRIORITY: Any
HAS_CPU_AFFINITY: Any
CLOCK_TICKS: Any
PAGESIZE: Any
BOOT_TIME: Any
BIGFILE_BUFFERING: Any
LITTLE_ENDIAN: Any
DISK_SECTOR_SIZE: int
AF_LINK: Any
AddressFamily: Any
IOPRIO_CLASS_NONE: int
IOPRIO_CLASS_RT: int
IOPRIO_CLASS_BE: int
IOPRIO_CLASS_IDLE: int

class IOPriority(enum.IntEnum):
    IOPRIO_CLASS_NONE: int = ...
    IOPRIO_CLASS_RT: int = ...
    IOPRIO_CLASS_BE: int = ...
    IOPRIO_CLASS_IDLE: int = ...

PROC_STATUSES: Any
TCP_STATUSES: Any

svmem = namedtuple('svmem', ['total', 'available', 'percent', 'used', 'free', 'active', 'inactive', 'buffers', 'cached', 'shared', 'slab'])

sdiskio = namedtuple('sdiskio', ['read_count', 'write_count', 'read_bytes', 'write_bytes', 'read_time', 'write_time', 'read_merged_count', 'write_merged_count', 'busy_time'])

popenfile = namedtuple('popenfile', ['path', 'fd', 'position', 'mode', 'flags'])

pmem = namedtuple('pmem', 'rss vms shared text lib data dirty')

pfullmem: Any
pmmap_grouped = namedtuple('pmmap_grouped', ['path', 'rss', 'size', 'pss', 'shared_clean', 'shared_dirty', 'private_clean', 'private_dirty', 'referenced', 'anonymous', 'swap'])

pmmap_ext: Any
pio = namedtuple('pio', ['read_count', 'write_count', 'read_bytes', 'write_bytes', 'read_chars', 'write_chars'])

pcputimes = namedtuple('pcputimes', ['user', 'system', 'children_user', 'children_system', 'iowait'])

def readlink(path: Any): ...
def file_flags_to_mode(flags: Any): ...
def is_storage_device(name: Any): ...
def set_scputimes_ntuple(procfs_path: Any) -> None: ...
def cat(fname: Any, fallback: Any = ..., binary: bool = ...): ...

scputimes: Any

def calculate_avail_vmem(mems: Any): ...
def virtual_memory(): ...
def swap_memory(): ...
def cpu_times(): ...
def per_cpu_times(): ...
def cpu_count_logical(): ...
def cpu_count_physical(): ...
def cpu_stats(): ...
def cpu_freq(): ...

net_if_addrs: Any

class _Ipv6UnsupportedError(Exception): ...

class Connections:
    tmap: Any = ...
    def __init__(self) -> None: ...
    def get_proc_inodes(self, pid: Any): ...
    def get_all_inodes(self): ...
    @staticmethod
    def decode_address(addr: Any, family: Any): ...
    @staticmethod
    def process_inet(file: Any, family: Any, type_: Any, inodes: Any, filter_pid: Optional[Any] = ...) -> None: ...
    @staticmethod
    def process_unix(file: Any, family: Any, inodes: Any, filter_pid: Optional[Any] = ...) -> None: ...
    def retrieve(self, kind: Any, pid: Optional[Any] = ...): ...

def net_connections(kind: str = ...): ...
def net_io_counters(): ...
def net_if_stats(): ...

disk_usage: Any

def disk_io_counters(perdisk: bool = ...): ...
def disk_partitions(all: bool = ...): ...
def sensors_temperatures(): ...
def sensors_fans(): ...
def sensors_battery(): ...
def users(): ...
def boot_time(): ...
def pids(): ...
def pid_exists(pid: Any): ...
def ppid_map(): ...
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
    def terminal(self): ...
    def io_counters(self): ...
    def cpu_times(self): ...
    def cpu_num(self): ...
    def wait(self, timeout: Optional[Any] = ...): ...
    def create_time(self): ...
    def memory_info(self): ...
    def memory_full_info(self, _private_re: Any = ..., _pss_re: Any = ..., _swap_re: Any = ...): ...
    memory_full_info: Any = ...
    def memory_maps(self): ...
    def cwd(self): ...
    def num_ctx_switches(self, _ctxsw_re: Any = ...): ...
    def num_threads(self, _num_threads_re: Any = ...): ...
    def threads(self): ...
    def nice_get(self): ...
    def nice_set(self, value: Any): ...
    def cpu_affinity_get(self): ...
    def cpu_affinity_set(self, cpus: Any) -> None: ...
    def ionice_get(self): ...
    def ionice_set(self, ioclass: Any, value: Any): ...
    def rlimit(self, resource: Any, limits: Optional[Any] = ...): ...
    def status(self): ...
    def open_files(self): ...
    def connections(self, kind: str = ...): ...
    def num_fds(self): ...
    def ppid(self): ...
    def uids(self, _uids_re: Any = ...): ...
    def gids(self, _gids_re: Any = ...): ...
