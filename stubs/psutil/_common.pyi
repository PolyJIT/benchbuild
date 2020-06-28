import enum
from collections import namedtuple
from socket import AF_INET6 as AF_INET6
from typing import Any, Optional

POSIX: Any
WINDOWS: Any
LINUX: Any
MACOS: Any
OSX = MACOS
FREEBSD: Any
OPENBSD: Any
NETBSD: Any
BSD: Any
SUNOS: Any
STATUS_RUNNING: str
STATUS_SLEEPING: str
STATUS_DISK_SLEEP: str
STATUS_STOPPED: str
STATUS_TRACING_STOP: str
STATUS_ZOMBIE: str
STATUS_DEAD: str
STATUS_WAKE_KILL: str
STATUS_WAKING: str
STATUS_IDLE: str
STATUS_LOCKED: str
STATUS_WAITING: str
STATUS_SUSPENDED: str
STATUS_PARKED: str
CONN_ESTABLISHED: str
CONN_SYN_SENT: str
CONN_SYN_RECV: str
CONN_FIN_WAIT1: str
CONN_FIN_WAIT2: str
CONN_TIME_WAIT: str
CONN_CLOSE: str
CONN_CLOSE_WAIT: str
CONN_LAST_ACK: str
CONN_LISTEN: str
CONN_CLOSING: str
CONN_NONE: str
NIC_DUPLEX_FULL: int
NIC_DUPLEX_HALF: int
NIC_DUPLEX_UNKNOWN: int

class NicDuplex(enum.IntEnum):
    NIC_DUPLEX_FULL: int = ...
    NIC_DUPLEX_HALF: int = ...
    NIC_DUPLEX_UNKNOWN: int = ...

class BatteryTime(enum.IntEnum):
    POWER_TIME_UNKNOWN: int = ...
    POWER_TIME_UNLIMITED: int = ...

ENCODING: Any
ENCODING_ERRS: Any

sswap = namedtuple('sswap', ['total', 'used', 'free', 'percent', 'sin', 'sout'])

sdiskusage = namedtuple('sdiskusage', ['total', 'used', 'free', 'percent'])

sdiskio = namedtuple('sdiskio', ['read_count', 'write_count', 'read_bytes', 'write_bytes', 'read_time', 'write_time'])

sdiskpart = namedtuple('sdiskpart', ['device', 'mountpoint', 'fstype', 'opts'])

snetio = namedtuple('snetio', ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv', 'errin', 'errout', 'dropin', 'dropout'])

suser = namedtuple('suser', ['name', 'terminal', 'host', 'started', 'pid'])

sconn = namedtuple('sconn', ['fd', 'family', 'type', 'laddr', 'raddr', 'status', 'pid'])

snicaddr = namedtuple('snicaddr', ['family', 'address', 'netmask', 'broadcast', 'ptp'])

snicstats = namedtuple('snicstats', ['isup', 'duplex', 'speed', 'mtu'])

scpustats = namedtuple('scpustats', ['ctx_switches', 'interrupts', 'soft_interrupts', 'syscalls'])

scpufreq = namedtuple('scpufreq', ['current', 'min', 'max'])

shwtemp = namedtuple('shwtemp', ['label', 'current', 'high', 'critical'])

sbattery = namedtuple('sbattery', ['percent', 'secsleft', 'power_plugged'])

sfan = namedtuple('sfan', ['label', 'current'])

pcputimes = namedtuple('pcputimes', ['user', 'system', 'children_user', 'children_system'])

popenfile = namedtuple('popenfile', ['path', 'fd'])

pthread = namedtuple('pthread', ['id', 'user_time', 'system_time'])

puids = namedtuple('puids', ['real', 'effective', 'saved'])

pgids = namedtuple('pgids', ['real', 'effective', 'saved'])

pio = namedtuple('pio', ['read_count', 'write_count', 'read_bytes', 'write_bytes'])

pionice = namedtuple('pionice', ['ioclass', 'value'])

pctxsw = namedtuple('pctxsw', ['voluntary', 'involuntary'])

pconn = namedtuple('pconn', ['fd', 'family', 'type', 'laddr', 'raddr', 'status'])

addr = namedtuple('addr', ['ip', 'port'])
conn_tmap: Any

class Error(Exception):
    __module__: str = ...
    msg: Any = ...
    def __init__(self, msg: str = ...) -> None: ...

class NoSuchProcess(Error):
    __module__: str = ...
    pid: Any = ...
    name: Any = ...
    msg: Any = ...
    def __init__(self, pid: Any, name: Optional[Any] = ..., msg: Optional[Any] = ...) -> None: ...
    def __path__(self): ...

class ZombieProcess(NoSuchProcess):
    __module__: str = ...
    pid: Any = ...
    ppid: Any = ...
    name: Any = ...
    msg: Any = ...
    def __init__(self, pid: Any, name: Optional[Any] = ..., ppid: Optional[Any] = ..., msg: Optional[Any] = ...) -> None: ...

class AccessDenied(Error):
    __module__: str = ...
    pid: Any = ...
    name: Any = ...
    msg: Any = ...
    def __init__(self, pid: Optional[Any] = ..., name: Optional[Any] = ..., msg: Optional[Any] = ...) -> None: ...

class TimeoutExpired(Error):
    __module__: str = ...
    seconds: Any = ...
    pid: Any = ...
    name: Any = ...
    def __init__(self, seconds: Any, pid: Optional[Any] = ..., name: Optional[Any] = ...) -> None: ...

def usage_percent(used: Any, total: Any, round_: Optional[Any] = ...): ...
def memoize(fun: Any): ...
def isfile_strict(path: Any): ...
def path_exists_strict(path: Any): ...
def supports_ipv6(): ...
def parse_environ_block(data: Any): ...
def sockfam_to_enum(num: Any): ...
def socktype_to_enum(num: Any): ...
def conn_to_ntuple(fd: Any, fam: Any, type_: Any, laddr: Any, raddr: Any, status: Any, status_map: Any, pid: Optional[Any] = ...): ...
def deprecated_method(replacement: Any): ...

class _WrapNumbers:
    lock: Any = ...
    cache: Any = ...
    reminders: Any = ...
    reminder_keys: Any = ...
    def __init__(self) -> None: ...
    def run(self, input_dict: Any, name: Any): ...
    def cache_clear(self, name: Optional[Any] = ...) -> None: ...
    def cache_info(self): ...

def wrap_numbers(input_dict: Any, name: Any): ...
def bytes2human(n: Any, format: str = ...): ...
def term_supports_colors(file: Any = ...): ...
def hilite(s: Any, color: str = ..., bold: bool = ...): ...
def print_color(s: Any, color: str = ..., bold: bool = ..., file: Any = ...) -> None: ...
def debug(msg: Any) -> None: ...

# Names in __all__ with no definition:
#   pconn
#   pcputimes
#   pctxsw
#   pgids
#   pio
#   pionice
#   popenfile
#   pthread
#   puids
#   sconn
#   scpustats
#   sdiskio
#   sdiskpart
#   sdiskusage
#   snetio
#   snicaddr
#   snicstats
#   sswap
#   suser
