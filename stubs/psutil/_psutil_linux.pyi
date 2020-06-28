from typing import Any

DUPLEX_FULL: int
DUPLEX_HALF: int
DUPLEX_UNKNOWN: int
RLIMIT_AS: int
RLIMIT_CORE: int
RLIMIT_CPU: int
RLIMIT_DATA: int
RLIMIT_FSIZE: int
RLIMIT_LOCKS: int
RLIMIT_MEMLOCK: int
RLIMIT_MSGQUEUE: int
RLIMIT_NICE: int
RLIMIT_NOFILE: int
RLIMIT_NPROC: int
RLIMIT_RSS: int
RLIMIT_RTPRIO: int
RLIMIT_RTTIME: int
RLIMIT_SIGPENDING: int
RLIMIT_STACK: int
RLIM_INFINITY: int
version: int

def disk_partitions(*args, **kwargs) -> Any: ...
def linux_prlimit(*args, **kwargs) -> Any: ...
def linux_sysinfo(*args, **kwargs) -> Any: ...
def net_if_duplex_speed(*args, **kwargs) -> Any: ...
def proc_cpu_affinity_get(*args, **kwargs) -> Any: ...
def proc_cpu_affinity_set(*args, **kwargs) -> Any: ...
def proc_ioprio_get(*args, **kwargs) -> Any: ...
def proc_ioprio_set(*args, **kwargs) -> Any: ...
def set_testing(*args, **kwargs) -> Any: ...
def users(*args, **kwargs) -> Any: ...
