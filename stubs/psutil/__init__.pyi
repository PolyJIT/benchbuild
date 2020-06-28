import os
from ._common import AIX as AIX, AccessDenied as AccessDenied, BSD as BSD, CONN_CLOSE as CONN_CLOSE, CONN_CLOSE_WAIT as CONN_CLOSE_WAIT, CONN_CLOSING as CONN_CLOSING, CONN_ESTABLISHED as CONN_ESTABLISHED, CONN_FIN_WAIT1 as CONN_FIN_WAIT1, CONN_FIN_WAIT2 as CONN_FIN_WAIT2, CONN_LAST_ACK as CONN_LAST_ACK, CONN_LISTEN as CONN_LISTEN, CONN_NONE as CONN_NONE, CONN_SYN_RECV as CONN_SYN_RECV, CONN_SYN_SENT as CONN_SYN_SENT, CONN_TIME_WAIT as CONN_TIME_WAIT, Error as Error, FREEBSD as FREEBSD, LINUX as LINUX, MACOS as MACOS, NETBSD as NETBSD, NIC_DUPLEX_FULL as NIC_DUPLEX_FULL, NIC_DUPLEX_HALF as NIC_DUPLEX_HALF, NIC_DUPLEX_UNKNOWN as NIC_DUPLEX_UNKNOWN, NoSuchProcess as NoSuchProcess, OPENBSD as OPENBSD, OSX as OSX, POSIX as POSIX, STATUS_DEAD as STATUS_DEAD, STATUS_DISK_SLEEP as STATUS_DISK_SLEEP, STATUS_IDLE as STATUS_IDLE, STATUS_LOCKED as STATUS_LOCKED, STATUS_PARKED as STATUS_PARKED, STATUS_RUNNING as STATUS_RUNNING, STATUS_SLEEPING as STATUS_SLEEPING, STATUS_STOPPED as STATUS_STOPPED, STATUS_TRACING_STOP as STATUS_TRACING_STOP, STATUS_WAITING as STATUS_WAITING, STATUS_WAKING as STATUS_WAKING, STATUS_ZOMBIE as STATUS_ZOMBIE, SUNOS as SUNOS, TimeoutExpired as TimeoutExpired, WINDOWS as WINDOWS, ZombieProcess as ZombieProcess
from ._pslinux import IOPRIO_CLASS_BE as IOPRIO_CLASS_BE, IOPRIO_CLASS_IDLE as IOPRIO_CLASS_IDLE, IOPRIO_CLASS_NONE as IOPRIO_CLASS_NONE, IOPRIO_CLASS_RT as IOPRIO_CLASS_RT
from ._psutil_linux import RLIMIT_AS as RLIMIT_AS, RLIMIT_CORE as RLIMIT_CORE, RLIMIT_CPU as RLIMIT_CPU, RLIMIT_DATA as RLIMIT_DATA, RLIMIT_FSIZE as RLIMIT_FSIZE, RLIMIT_LOCKS as RLIMIT_LOCKS, RLIMIT_MEMLOCK as RLIMIT_MEMLOCK, RLIMIT_NOFILE as RLIMIT_NOFILE, RLIMIT_NPROC as RLIMIT_NPROC, RLIMIT_RSS as RLIMIT_RSS, RLIMIT_STACK as RLIMIT_STACK, RLIM_INFINITY as RLIM_INFINITY
from typing import Any, Optional

PROCFS_PATH: str
RLIMIT_MSGQUEUE: Any
RLIMIT_NICE: Any
RLIMIT_RTPRIO: Any
RLIMIT_RTTIME: Any
RLIMIT_SIGPENDING: Any
version_info: Any
AF_LINK: Any
POWER_TIME_UNLIMITED: Any
POWER_TIME_UNKNOWN: Any

class Process:
    def __init__(self, pid: Optional[Any] = ...) -> None: ...
    def __eq__(self, other: Any) -> Any: ...
    def __ne__(self, other: Any) -> Any: ...
    def __hash__(self) -> Any: ...
    @property
    def pid(self): ...
    def oneshot(self) -> None: ...
    def as_dict(self, attrs: Optional[Any] = ..., ad_value: Optional[Any] = ...): ...
    def parent(self): ...
    def parents(self): ...
    def is_running(self): ...
    def ppid(self): ...
    def name(self): ...
    def exe(self): ...
    def cmdline(self): ...
    def status(self): ...
    def username(self): ...
    def create_time(self): ...
    def cwd(self): ...
    def nice(self, value: Optional[Any] = ...): ...
    def uids(self): ...
    def gids(self): ...
    def terminal(self): ...
    def num_fds(self): ...
    def io_counters(self): ...
    def ionice(self, ioclass: Optional[Any] = ..., value: Optional[Any] = ...): ...
    def rlimit(self, resource: Any, limits: Optional[Any] = ...): ...
    def cpu_affinity(self, cpus: Optional[Any] = ...): ...
    def cpu_num(self): ...
    def environ(self): ...
    def num_handles(self): ...
    def num_ctx_switches(self): ...
    def num_threads(self): ...
    def threads(self): ...
    def children(self, recursive: bool = ...): ...
    def cpu_percent(self, interval: Optional[Any] = ...): ...
    def cpu_times(self): ...
    def memory_info(self): ...
    def memory_info_ex(self): ...
    def memory_full_info(self): ...
    def memory_percent(self, memtype: str = ...): ...
    def memory_maps(self, grouped: bool = ...): ...
    def open_files(self): ...
    def connections(self, kind: str = ...): ...
    def send_signal(self, sig: Any) -> None: ...
    def suspend(self) -> None: ...
    def resume(self) -> None: ...
    def terminate(self) -> None: ...
    def kill(self) -> None: ...
    def wait(self, timeout: Optional[Any] = ...): ...

class Popen(Process):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def __dir__(self): ...
    def __enter__(self): ...
    def __exit__(self, *args: Any, **kwargs: Any): ...
    def __getattribute__(self, name: Any): ...
    def wait(self, timeout: Optional[Any] = ...): ...

def pids(): ...
def pid_exists(pid: Any): ...
def process_iter(attrs: Optional[Any] = ..., ad_value: Optional[Any] = ...): ...
def wait_procs(procs: Any, timeout: Optional[Any] = ..., callback: Optional[Any] = ...): ...
def cpu_count(logical: bool = ...): ...
def cpu_times(percpu: bool = ...): ...
def cpu_percent(interval: Optional[Any] = ..., percpu: bool = ...): ...
def cpu_times_percent(interval: Optional[Any] = ..., percpu: bool = ...): ...
def cpu_stats(): ...
def cpu_freq(percpu: bool = ...): ...
getloadavg = os.getloadavg

def virtual_memory(): ...
def swap_memory(): ...
def disk_usage(path: Any): ...
def disk_partitions(all: bool = ...): ...
def disk_io_counters(perdisk: bool = ..., nowrap: bool = ...): ...
def net_io_counters(pernic: bool = ..., nowrap: bool = ...): ...
def net_connections(kind: str = ...): ...
def net_if_addrs(): ...
def net_if_stats(): ...
def sensors_temperatures(fahrenheit: bool = ...): ...
def sensors_fans(): ...
def sensors_battery(): ...
def boot_time(): ...
def users(): ...

# Names in __all__ with no definition:
#   __version__
