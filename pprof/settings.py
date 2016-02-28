"""
Settings module for pprof.

All settings are stored in a simple dictionary. Each
setting should be modifiable via environment variable.
"""
import json
import os
import uuid
import re
import warnings
from datetime import datetime


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

    # Linux
    try:
        res = open('/proc/cpuinfo').read().count('processor\t:')

        if res > 0:
            return res
    except IOError:
        pass

    raise Exception('Can not determine number of CPUs on this system')


class InvalidConfigKey(RuntimeWarning):

    """Warn, if you access a non-existing key pprof's configuration."""

    pass


class UUIDEncoder(json.JSONEncoder):
    """Encoder module for UUID objects."""

    def default(self, obj):
        """Encode UUID objects as string."""
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class Configuration():
    def __init__(self, parent_key, node=None, parent=None, init=True):
        self.parent = parent
        self.id = parent_key
        self.node = node if node is not None else {}
        if init:
            self.init_from_env()

    def store(self, to):
        with open(to, 'w') as outf:
            json.dump(self.node, outf, cls=UUIDEncoder, indent=True)

    def load(self, _from):
        if os.path.exists(_from):
            with open(_from, 'r') as inf:
                self.node = json.load(inf)

    def register(self, key, subtree):
        self[key] = subtree

    def __getitem__(self, key):
        if not key in self.node:
            warnings.warn(
                "Access to non-existing config element: {}".format(key),
                category=InvalidConfigKey,
                stacklevel=2)
            return Configuration(key, init=False)
        return Configuration(key, parent=self, node=self.node[key], init=False)

    def __to_env_var__(self):
        if self.parent:
            return (self.parent.__to_env_var__() + "_" + self.id).upper()
        return self.id.upper()

    def init_from_env(self):
        if 'default' in self.node:
            env_var = self.__to_env_var__().upper()
            self.node['value'] = getenv(env_var, self.node['default'])
        else:
            if isinstance(self.node, dict):
                for k in self.node:
                    self[k].init_from_env()

    def __setitem__(self, key, val):
        if key in self.node:
            self.node[key]['value'] = val
        else:
            if isinstance(val, dict):
                self.node[key] = val
                self[key].init_from_env()
            else:
                self.node[key] = {'value': val}

    def __contains__(self, key):
        return key in self.node

    def __str__(self):
        if 'value' in self.node:
            return str(self.node['value'])
        else:
            warnings.warn("Tried to get the str() value of an inner node.",
                          stacklevel=2)
            return str(self.node)

    def __repr__(self):
        _repr = []
        if 'value' in self.node:
            return self.__to_env_var__() + " = " + repr(self.node['value'])
        if 'default' in self.node:
            return self.__to_env_var__() + " = {DEFAULT} " + repr(self.node[
                'default'])

        for k in self.node:
            _repr.append(repr(self[k]))

        return "\n".join(_repr)

    def update(self, cfg_dict):
        self.node.update(cfg_dict.node)

# Initialize the global configuration once.
CFG = Configuration(
    "pprof",
    node={
        "src_dir": {
            "desc":
            "source directory of pprof. Usually the git repo root dir.",
            "default": os.getcwd()
        },
        "build_dir": {
            "desc": "build directory of pprof. All intermediate projects will "
                    "be placed here",
            "default": os.path.join(os.getcwd(), "results")
        },
        "test_dir": {
            "desc":
            "Additional test inputs, required for (some) run-time tests."
            "These can be obtained from the a different repo. Most "
            "projects don't need it",
            "default": os.path.join(os.getcwd(), "testinputs")
        },
        "tmp_dir": {
            "desc": "Temporary dir. This will be used for caching downloads.",
            "default": os.path.join(os.getcwd(), "tmp")
        },
        "path": {
            "desc": "Additional PATH variable for pprof.",
            "default": ""
        },
        "ld_library_path": {
            "desc": "Additional library path for pprof.",
            "default": ""
        },
        "jobs": {
            "desc":
            "Number of jobs that can be used for building and running.",
            "default": str(available_cpu_count())
        },
        "experiment": {
            "desc":
            "The experiment UUID we run everything under. This groups the project "
            "runs in the database.",
            "default": str(uuid.uuid4())
        },
        "local_build": {
            "desc": "Perform a local build on the cluster nodes.",
            "default": False
        },
        "keep": {
            "default": False,
        },
        "experiment_description": {
            "default": str(datetime.now())
        },
        "regression_prefix": {
            "default": os.path.join("/", "tmp", "pprof-regressions")
        },
        "pprof_prefix": {
            "default": os.getcwd()
        },
        "pprof_ebuild": {
            "default": ""
        },
        "mail": {
            "desc": "E-Mail address dedicated to pprof.",
            "default": None
        }
    })

CFG["llvm"] = {
    "dir": {
        "desc": "Path to LLVM. This will be required.",
        "default": os.path.join(os.getcwd(), "install")
    },
    "src": {
        "default": os.path.join(os.getcwd(), "pprof-llvm")
    },
}

CFG["papi"] = {
    "include": {
        "desc": "libpapi include path.",
        "default": "/usr/include"
    },
    "library": {
        "desc": "libpapi library path.",
        "default": "/usr/lib"
    }
}

CFG["likwid"] = {
    "prefix": {
        "desc": "Prefix to which the likwid library was installed.",
        "default": "/usr/"
    },
}

CFG["repo"] = {
    "llvm": {
        "url": {"default": "http://llvm.org/git/llvm.git"},
        "branch": {"default": "master"},
        "commit_hash": {"default": None}
    },
    "polly": {
        "url": {"default": "http://github.com/simbuerg/polly.git"},
        "branch": {"default": "devel"},
        "commit_hash": {"default": None}
    },
    "clang": {
        "url": {"default": "http://llvm.org/git/clang.git"},
        "branch": {"default": "master"},
        "commit_hash": {"default": None}
    },
    "polli": {
        "url": {"default": "http://github.com/simbuerg/polli.git"},
        "branch": {"default": "master"},
        "commit_hash": {"default": None}
    },
    "openmp": {
        "url": {"default": "http://llvm.org/git/openmp.git"},
        "branch": {"default": "master"},
        "commit_hash": {"default": None}
    },
}

CFG.init_from_env()
