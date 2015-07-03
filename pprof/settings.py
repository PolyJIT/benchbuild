"""
Settings module for pprof.

All settings are stored in a simple dictionary. Each
setting should be modifiable via environment variable.
"""
import os
import re
import subprocess
from uuid import uuid4
from os import getenv
import json

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


def load_config(config_path, config):
    """
    Load pprof's configuration from a config file.

    :config_path
        Path where we find our configuration.
    :config
        Dictionary where our configuration should be loaded into.
    :return
        True, if we could load the configuration successfully.
    """
    with open(config_path) as config_file:
        globs, locs = {}, {}
        execfile(config_path, globs, locs)
        out_config = locs["config"]

        if not isinstance(out_config, dict):
            print("Config file " + config_path + " does not specify a config object.")
            return False

        # Merge in only the settings that were specified
        for key in out_config.keys():
            config[key] = out_config[key]

        return True

config_metadata = [
    {
        "name": "sourcedir",
        "desc": "TODO",
        "env": "PPROF_SRC_DIR",
        "default": os.getcwd()
    },
    {
        "name": "builddir",
        "desc": "TODO",
        "env": "PPROF_OBJ_DIR",
        "default": os.path.join(os.getcwd(), "results")
    },
    {
        "name": "testdir",
        "desc": "TODO",
        "env": "PPROF_TESTINPUTS",
        "default": os.path.join(os.getcwd(), "testinputs")
    },
    {
        "name": "llvmdir",
        "desc": "TODO",
        "env": "PPROF_LLVM_DIR",
        "default": os.path.join(os.getcwd(), "install")
    },
    {
        "name": "tmpdir",
        "desc": "TODO",
        "env": "PPROF_TMP_DIR",
        "default": os.path.join(os.getcwd(), "tmp")
    },
    {
        "name": "path",
        "desc": "TODO",
        "env": "PATH",
        "default": ""
    },
    {
        "name": "nodedir",
        "desc": "TODO",
        "env": "PPROF_CLUSTER_NODEDIR",
        "default": os.path.join(os.getcwd(), "results")
    },
    {
        "name": "ld_library_path",
        "desc": "TODO",
        "env": "LD_LIBRARY_PATH",
        "default": ""
    },
    {
        "name": "jobs",
        "desc": "TODO",
        "env": "PPROF_MAKE_JOBS",
        "default": str(available_cpu_count())
    },
    {
        "name": "experiment",
        "desc": "TODO",
        "env": "PPROF_EXPERIMENT_ID",
        "default": uuid4()
    },
    {
        "name": "db_host",
        "desc": "TODO",
        "env": "PPROF_DB_HOST",
        "default": "localhost"
    },
    {
        "name": "db_port",
        "desc": "TODO",
        "env": "PPROF_DB_PORT",
        "default": 5432
    },
    {
        "name": "db_name",
        "desc": "TODO",
        "env": "PPROF_DB_NAME",
        "default": "pprof"
    },
    {
        "name": "db_user",
        "desc": "TODO",
        "env": "PPROF_DB_USER",
        "default": "pprof"
    },
    {
        "name": "db_pass",
        "desc": "TODO",
        "env": "PPROF_DB_PASS",
        "default": "pprof"
    },
    {
        "name": "slurm_script",
        "desc": "TODO",
        "env": "PPROF_CLUSTER_SCRIPT_NAME",
        "default": "chimaira-slurm.sh"
    },
    {
        "name": "cpus-per-task",
        "desc": "TODO",
        "env": "PPROF_CLUSTER_CPUS_PER_TASK",
        "default": 10
    },
    {
        "name": "local_build",
        "env": "PPROF_CLUSTER_BUILD_LOCAL",
        "default": False
    },
    {
        "name": "account",
        "env": "PPROF_CLUSTER_ACCOUNT",
        "default": "cl"
    },
    {
        "name": "partition",
        "env": "PPROF_CLUSTER_PARTITION",
        "default": "chimaira"
    },
    {
        "name": "llvm_repo",
        "default": { "url": "http://llvm.org/git/llvm.git", "branch": None }
    },
    {
        "name": "polly_repo",
        "default": { "url": "http://github.com/simbuerg/polly.git", "branch": "devel" }
    },
    {
        "name": "clang_repo",
        "default": { "url": "http://llvm.org/git/clang.git", "branch": None }
    },
    {
        "name": "polli_repo",
        "default": { "url": "http://github.com/simbuerg/polli.git", "branch": None }
    }
]

def default_config(config_metadata):
    config = {}
    for setting in config_metadata:
        if "env" in setting:
            config[setting["name"]] = getenv(setting["env"], setting["default"])
        else:
            config[setting["name"]] = setting["default"]
    return config

config = default_config(config_metadata)
