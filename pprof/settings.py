"""
Settings module for pprof.

All settings are stored in a simple dictionary. Each
setting should be modifiable via environment variable.
"""
import os
import re
import subprocess
from uuid import uuid4
from os import getenv as e


def available_cpu_count():
    """
    Get the number of available CPUs.

    Number of available virtual or physical CPUs on this system, i.e.
    user/real as output by time(1) when called with an optimally scaling
    userspace-only program.

    :return:
        Number of avaialable CPUs.
    """
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
    "sourcedir": e("PPROF_SRC_DIR", os.getcwd()),
    "builddir": e("PPROF_OBJ_DIR", os.path.join(os.getcwd(), "results")),
    "testdir": e("PPROF_TESTINPUTS", os.path.join(os.getcwd(), "testinputs")),
    "llvmdir": e("PPROF_LLVM_DIR", os.path.join(os.getcwd(), "install")),
    "likwiddir": e("PPROF_LIKWID_DIR", os.getcwd()),
    "tmpdir": e("PPROF_TMP_DIR", os.path.join(os.getcwd(), "tmp")),
    "path": e("PATH", ""),
    "ld_library_path": e("LD_LIBRARY_PATH", ""),
    "jobs": e("PPROF_MAKE_JOBS", str(available_cpu_count())),
    "experiment": e("PPROF_EXPERIMENT_ID", uuid4()),
    "db_host": e("PPROF_DB_HOST", "localhost"),
    "db_port": e("PPROF_DB_PORT", 5432),
    "db_name": e("PPROF_DB_NAME", "pprof"),
    "db_user": e("PPROF_DB_USER", "pprof"),
    "db_pass": e("PPROF_DB_PASS", "pprof"),
    "nodedir": e("PPROF_CLUSTER_NODEDIR",
                 os.path.join(os.getcwd(), "results")),
    "slurm_script": e("PPROF_CLUSTER_SCRIPT_NAME", "chimaira-slurm.sh"),
    "cpus-per-task": e("PPROF_CLUSTER_CPUS_PER_TASK", 10),
    "local_build": e("PPROF_CLUSTER_BUILD_LOCAL", False),
    "account": e("PPROF_CLUSTER_ACCOUNT", "cl"),
    "partition": e("PPROF_CLUSTER_PARTITION", "chimaira"),
}
