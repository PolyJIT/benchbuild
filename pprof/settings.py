import os
import re
import subprocess
from uuid import uuid4

def available_cpu_count():
    """ Number of available virtual or physical CPUs on this system, i.e.
    user/real as output by time(1) when called with an optimally scaling
    userspace-only program"""

    # cpuset
    # cpuset may restrict the number of *available* processors
    try:
        m = re.search(r'(?m)^Cpus_allowed:\s*(.*)$',
                      open('/proc/self/status').read())
        if m:
            res = bin(int(m.group(1).replace(',', ''), 16)).count('1')
            if res > 0:
                return res
    except IOError:
        pass

    # Python 2.6+
    try:
        import multiprocessing
        return multiprocessing.cpu_count()
    except (ImportError, NotImplementedError):
        pass

    # http://code.google.com/p/psutil/
    try:
        import psutil
        return psutil.cpu_count()   # psutil.NUM_CPUS on old versions
    except (ImportError, AttributeError):
        pass

    # POSIX
    try:
        res = int(os.sysconf('SC_NPROCESSORS_ONLN'))

        if res > 0:
            return res
    except (AttributeError, ValueError):
        pass

    # Windows
    try:
        res = int(os.environ['NUMBER_OF_PROCESSORS'])

        if res > 0:
            return res
    except (KeyError, ValueError):
        pass

    # jython
    try:
        from java.lang import Runtime
        runtime = Runtime.getRuntime()
        res = runtime.availableProcessors()
        if res > 0:
            return res
    except ImportError:
        pass

    # BSD
    try:
        sysctl = subprocess.Popen(['sysctl', '-n', 'hw.ncpu'],
                                  stdout=subprocess.PIPE)
        scStdout = sysctl.communicate()[0]
        res = int(scStdout)

        if res > 0:
            return res
    except (OSError, ValueError):
        pass

    # Linux
    try:
        res = open('/proc/cpuinfo').read().count('processor\t:')

        if res > 0:
            return res
    except IOError:
        pass

    # Solaris
    try:
        pseudoDevices = os.listdir('/devices/pseudo/')
        res = 0
        for pd in pseudoDevices:
            if re.match(r'^cpuid@[0-9]+$', pd):
                res += 1

        if res > 0:
            return res
    except OSError:
        pass

    # Other UNIXes (heuristic)
    try:
        try:
            dmesg = open('/var/run/dmesg.boot').read()
        except IOError:
            dmesgProcess = subprocess.Popen(['dmesg'], stdout=subprocess.PIPE)
            dmesg = dmesgProcess.communicate()[0]

        res = 0
        while '\ncpu' + str(res) + ':' in dmesg:
            res += 1

        if res > 0:
            return res
    except OSError:
        pass

    raise Exception('Can not determine number of CPUs on this system')


config = {
    "sourcedir": os.getenv("PPROF_SRC_DIR", os.getcwd()),
    "builddir": os.getenv("PPROF_OBJ_DIR", os.path.join(os.getcwd(), "results")),
    "testdir": os.getenv("PPROF_TESTINPUTS", os.path.join(os.getcwd(), "testinputs")),
    "llvmdir": os.getenv("PPROF_LLVM_DIR", os.path.join(os.getcwd(), "install")),
    "likwiddir": os.getenv("PPROF_LIKWID_DIR", os.path.join(os.getcwd(), "bin")),
    "tmpdir": os.getenv("PPROF_TMP_DIR", os.path.join(os.getcwd(), "tmp")),
    "path": os.environ["PATH"],
    "ld_library_path": os.environ["LD_LIBRARY_PATH"],
    "jobs" : str(available_cpu_count()),
    "experiment" : os.getenv("PPROF_EXPERIMENT_ID", uuid4())
}


def setup_db_config():
    global config

    config["db_host"] = "localhost"
    config["db_port"] = 49153
    config["db_name"] = "pprof"
    config["db_user"] = "pprof"
    config["db_pass"] = "pprof"

    db_host = os.environ.get("PPROF_DB_HOST")
    if db_host:
        config["db_host"] = db_host

    db_port = os.environ.get("PPROF_DB_PORT")
    if db_port:
        config["db_port"] = db_port

    db_name = os.environ.get("PPROF_DB_NAME")
    if db_name:
        config["db_name"] = db_name

    db_user = os.environ.get("PPROF_DB_USER")
    if db_user:
        config["db_user"] = db_user

    db_pass = os.environ.get("PPROF_DB_PASS")
    if db_pass:
        config["db_pass"] = db_pass


_db_connection = None


def get_db_connection():
    import psycopg2
    global _db_connection
    if not _db_connection:
        setup_db_config()
        _db_connection = psycopg2.connect(
            host=config["db_host"],
            port=config["db_port"],
            user=config["db_user"],
            password=config["db_pass"],
            database=config["db_name"]
        )
    return _db_connection
