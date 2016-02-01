"""
Settings module for pprof.

All settings are stored in a simple dictionary. Each
setting should be modifiable via environment variable.
"""
import os
import re
import subprocess
from datetime import datetime
from uuid import uuid4
from os import getenv


def available_cpu_count():
    """
    Get the number of available CPUs.

    Number of available virtual or physical CPUs on this system, i.e.
    user/real as output by time(1) when called with an optimally scaling
    userspace-only program.

    Returns:
        Number of avaialable CPUs.
    """
    # cpuset
    # cpuset may restrict the number of *available* processors
    try:
        match = re.search(r'(?m)^Cpus_allowed:\s*(.*)$',
                          open('/proc/self/status').read())
        if match:
            res = bin(int(match.group(1).replace(',', ''), 16)).count('1')
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
        return psutil.cpu_count()  # psutil.NUM_CPUS on old versions
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
        sysctl = subprocess.Popen(
            ['sysctl', '-n', 'hw.ncpu'],
            stdout=subprocess.PIPE)
        sc_stdout = sysctl.communicate()[0]
        res = int(sc_stdout)

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
        pseudo_devs = os.listdir('/devices/pseudo/')
        res = 0
        for pseudo_dev in pseudo_devs:
            if re.match(r'^cpuid@[0-9]+$', pseudo_dev):
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
            dmesg_proc = subprocess.Popen(['dmesg'], stdout=subprocess.PIPE)
            dmesg = dmesg_proc.communicate()[0]

        res = 0
        while '\ncpu' + str(res) + ':' in dmesg:
            res += 1

        if res > 0:
            return res
    except OSError:
        pass

    raise Exception('Can not determine number of CPUs on this system')


def load_config(config_path, new_config):
    """
    Load pprof's configuration from a config file.

    Args:
        config_path: Path where we find our configuration.
        new_config: Dictionary where our configuration should be loaded into.

    Return:
        True, if we could load the configuration successfully.
    """
    with open(config_path) as config_file:
        globs, locs = {}, {}
        exec (compile(
            open(config_path).read(), config_path, 'exec'), globs, locs)
        out_config = locs["config"]

        if not isinstance(out_config, dict):
            print(("Config file " + config_path +
                   " does not specify a config object."))
            return False

        # Merge in only the settings that were specified
        for key in list(out_config.keys()):
            new_config[key] = out_config[key]

        return True


CONFIG_METADATA = [
    {
        "name": "sourcedir",
        "desc": "Source directory of pprof. Usually the git repo root dir.",
        "env": "PPROF_SRC_DIR",
        "default": os.getcwd()
    }, {
        "name": "builddir",
        "desc": "Build directory of pprof. All intermediate projects will be"
                "placed here",
        "env": "PPROF_OBJ_DIR",
        "default": os.path.join(os.getcwd(), "results")
    }, {
        "name": "testdir",
        "desc": "Additional test inputs, required for (some) run-time tests."
                "These can be obtained from the a different repo. Most "
                "projects don't need it",
        "env": "PPROF_TESTINPUTS",
        "default": os.path.join(os.getcwd(), "testinputs")
    }, {
        "name": "llvmdir",
        "desc": "Path to LLVM. This will be required.",
        "env": "PPROF_LLVM_DIR",
        "default": os.path.join(os.getcwd(), "install")
    }, {
        "name": "likwiddir",
        "desc": "Prefix to which the likwid library was installed.",
        "env": "PPROF_LIKWID_DIR",
        "default": "/usr/"
    }, {
        "name": "tmpdir",
        "desc": "Temporary dir. This will be used for caching downloads.",
        "env": "PPROF_TMP_DIR",
        "default": os.path.join(os.getcwd(), "tmp")
    }, {
        "name": "path",
        "desc": "Additional PATH variable for pprof.",
        "env": "PATH",
        "default": ""
    }, {
        "name": "nodedir",
        "desc":
        "Node directory, when executing on a cluster node. This is not "
        "used by pprof directly, but by external scripts.",
        "env": "PPROF_CLUSTER_NODEDIR",
        "default": os.path.join(os.getcwd(), "results")
    }, {
        "name": "ld_library_path",
        "desc": "Additional library path for pprof.",
        "env": "LD_LIBRARY_PATH",
        "default": ""
    }, {
        "name": "jobs",
        "desc": "Number of jobs that can be used for building and running.",
        "env": "PPROF_MAKE_JOBS",
        "default": str(available_cpu_count())
    }, {
        "name": "experiment",
        "desc":
        "The experiment UUID we run everything under. This groups the project "
        "runs in the database.",
        "env": "PPROF_EXPERIMENT_ID",
        "default": uuid4()
    }, {
        "name": "db_host",
        "desc": "Host address of the database to connect to.",
        "env": "PPROF_DB_HOST",
        "default": "localhost"
    }, {
        "name": "db_port",
        "desc": "Port number of the database to connect to.",
        "env": "PPROF_DB_PORT",
        "default": 5432
    }, {
        "name": "db_name",
        "desc": "The name of the PostgreSQL database that will be used.",
        "env": "PPROF_DB_NAME",
        "default": "pprof"
    }, {
        "name": "db_user",
        "desc":
        "The name of the PostgreSQL user to connect to the database with.",
        "env": "PPROF_DB_USER",
        "default": "pprof"
    }, {
        "name": "db_pass",
        "desc":
        "The password for the PostgreSQL user used to connect to the database with.",
        "env": "PPROF_DB_PASS",
        "default": "pprof"
    }, {
        "name": "slurm_script",
        "desc":
        "Name of the script that can be passed to SLURM. Used by external tools.",
        "env": "PPROF_CLUSTER_SCRIPT_NAME",
        "default": "chimaira-slurm.sh"
    }, {
        "name": "cpus-per-task",
        "desc":
        "Number of CPUs that should be requested from SLURM. Used by external tools.",
        "env": "PPROF_CLUSTER_CPUS_PER_TASK",
        "default": 10
    }, {
        "name": "local_build",
        "env": "PPROF_CLUSTER_BUILD_LOCAL",
        "desc": "Perform a local build on the cluster nodes.",
        "default": False
    }, {
        "name": "account",
        "env": "PPROF_CLUSTER_ACCOUNT",
        "desc": "The SLURM account to use by default.",
        "default": "cl"
    }, {
        "name": "partition",
        "env": "PPROF_CLUSTER_PARTITION",
        "desc": "The SLURM partition to use by default.",
        "default": "chimaira"
    }, {
        "name": "llvm_repo",
        "default": {"url": "http://llvm.org/git/llvm.git",
                    "branch": None,
                    "commit_hash": None}
    }, {
        "name": "polly_repo",
        "default": {"url": "http://github.com/simbuerg/polly.git",
                    "branch": "devel",
                    "commit_hash": None}
    }, {
        "name": "clang_repo",
        "default": {"url": "http://llvm.org/git/clang.git",
                    "branch": None,
                    "commit_hash": None}
    }, {
        "name": "polli_repo",
        "default": {"url": "http://github.com/simbuerg/polli.git",
                    "branch": None,
                    "commit_hash": None}
    }, {
        "name": "openmp_repo",
        "default": {"url": "http://llvm.org/git/openmp.git",
                    "branch": None,
                    "commit_hash": None}
    }, {
        "name": "keep",
        "default": False,
        "env": "PPROF_KEEP_RESULTS"
    }, {
        "name": "llvm-srcdir",
        "env": "PPROF_LLVM_SRC_DIR",
        "default": os.path.join(os.getcwd(), "pprof-llvm")
    }, {
        "name": "experiment_description",
        "env": "PPROF_EXPERIMENT_DESCRIPTION",
        "default": str(datetime.now())
    }, {
        "name": "regression-prefix",
        "env": "PPROF_REGRESSION_PREFIX",
        "default": os.path.join("/", "tmp", "pprof-regressions")
    }, {
        "name": "pprof-prefix",
        "env": "PPROF_PREFIX",
        "default": os.getcwd()
    }
]


def default_config(config_metadata):
    """
    Fill the config object.

    Args:
        config_metadata (list(dict(str,_))): Contains a list of dictionaries
            which indicate the name, environment variable and default value
            for each configuration option of pprof.
            Environment settings take precedence over defaults and command line
            options take precedence over environment settings.

    Returns (dict(str, _)): Dictionary with all configuration options.
    """
    def_config = {}
    for setting in config_metadata:
        if "env" in setting:
            def_config[setting["name"]] = getenv(setting["env"],
                                                 setting["default"])
        else:
            def_config[setting["name"]] = setting["default"]
    return def_config


config = default_config(CONFIG_METADATA)


def print_settings(config):
    from logging import info
    for cfg in CONFIG_METADATA:
        env_str = cfg["env"] if "env" in cfg else "<env not available>"
        key = cfg["name"]
        default_str = cfg["default"] if "default" in cfg else "<no default>"
        print("    {:<30} = {} (key: {}) (default: {})".format(env_str, config[
            key], key, default_str))
