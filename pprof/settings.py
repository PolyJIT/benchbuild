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
    """
    Dictionary-like data structure to contain all configuration variables.

    This serves as a configuration dictionary throughout pprof. You can use
    it to access all configuration options that are available. Whenever the
    structure is updated with a new subtree, all variables defined in the
    new subtree are updated from the environment.

    Environment variables are generated from the tree paths automatically.
        CFG["build_dir"] becomes PPROF_BUILD_DIR
        CFG["llvm"]["dir"] becomes PPROF_LLVM_DIR

    The configuration can be stored/loaded as JSON.

    Examples:
        >>> from pprof import settings as s
        >>> c = s.Configuration('pprof')
        >>> c['test'] = 42
        >>> c['test']
        PPROF_TEST=42
        >>> str(c['test'])
        '42'
        >>> type(c['test'])
        <class 'pprof.settings.Configuration'>
    """

    def __init__(self, parent_key, node=None, parent=None, init=True):
        self.parent = parent
        self.parent_key = parent_key
        self.node = node if node is not None else {}
        if init:
            self.init_from_env()

    def store(self, config_file):
        """ Store the configuration dictionary to a file."""
        with open(config_file, 'w') as outf:
            json.dump(self.node, outf, cls=UUIDEncoder, indent=True)

    def load(self, _from):
        """Load the configuration dictionary from file."""
        def load_rec(inode, config):
            for k in config:
                if isinstance(config[k], dict):
                    if k in inode:
                        load_rec(inode[k], config[k])
                    else:
                        warnings.warn(
                            "Key {} is not part of the default config, "
                            "ignoring.".format(k),
                            category=InvalidConfigKey,
                            stacklevel=2)
                else:
                    inode[k] = config[k]

        if os.path.exists(_from):
            with open(_from, 'r') as inf:
                load_rec(self.node, json.load(inf))
                self['config_file'] = os.path.abspath(_from)

    def init_from_env(self):
        """
        Initialize this node from environment.

        If we're a leaf node, i.e., a node containing a dictionary that
        consist of a 'default' key, compute our env variable and initialize
        our value from the environment.
        Otherwise, init our children.
        """

        if 'default' in self.node:
            env_var = self.__to_env_var__().upper()
            if 'value' in self.node:
                env_val = os.getenv(env_var, self.node['value'])
            else:
                env_val = os.getenv(env_var, self.node['default'])
            try:
                self.node['value'] = json.loads(str(env_val))
            except ValueError:
                self.node['value'] = env_val
        else:
            if isinstance(self.node, dict):
                for k in self.node:
                    self[k].init_from_env()

    def update(self, cfg_dict):
        """
        Update the configuration dictionary with new content.

        This just delegates the update down to the internal data structure.
        No validation is done on the format, be sure you know what you do.

        Args:
            cfg_dict: A configuration dictionary.

        """
        self.node.update(cfg_dict.node)

    def value(self):
        """
        Return the node value, if we're a leaf node.

        Examples:
            >>> from pprof import settings as s
            >>> c = s.Configuration("test")
            >>> c['x'] = { "y" : { "value" : None }, "z" : { "value" : 2 }}
            >>> c['x']['y'].value() == None
            True
            >>> c['x']['z'].value()
            2
            >>> c['x'].value()
            TEST_X_Y=null
            TEST_X_Z=2

        """
        if 'value' in self.node:
            return self.node['value']
        else:
            return self

    def __getitem__(self, key):
        if not key in self.node:
            warnings.warn(
                "Access to non-existing config element: {}".format(key),
                category=InvalidConfigKey,
                stacklevel=2)
            return Configuration(key, init=False)
        return Configuration(key, parent=self, node=self.node[key], init=False)

    def __setitem__(self, key, val):
        if key in self.node:
            self.node[key]['value'] = val
        else:
            if isinstance(val, dict):
                self.node[key] = val
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
            return self.__to_env_var__() + "=" + json.dumps(self.node['value'])
        if 'default' in self.node:
            return self.__to_env_var__() + "=" + json.dumps(self.node[
                'default'])

        for k in self.node:
            _repr.append(repr(self[k]))

        return "\n".join(sorted(_repr))

    def __to_env_var__(self):
        if self.parent:
            return (
                self.parent.__to_env_var__() + "_" + self.parent_key).upper()
        return self.parent_key.upper()

# Initialize the global configuration once.
CFG = Configuration(
    "pprof",
    node={
        "config_file": {
            "desc": "Config file path of pprof. Not guaranteed to exist.",
            "default": os.path.join(os.curdir, ".pprof.json"),
        },
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
        "clean": {
            "default": True,
            "desc": "Clean temporary objects, after completion.",
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

CFG['db'] = {
    "host": {
        "desc": "host name of our db.",
        "default": "localhost"
    },
    "port": {
        "desc": "port to connect to the database",
        "default": 5432
    },
    "name": {
        "desc": "The name of the PostgreSQL database that will be used.",
        "default": "pprof"
    },
    "user": {
        "desc":
        "The name of the PostgreSQL user to connect to the database with.",
        "default": "pprof"
    },
    "pass": {
        "desc":
        "The password for the PostgreSQL user used to connect to the database with.",
        "default": "pprof"
    },
    "rollback": {
        "desc": "Rollback all operations after pprof completes.",
        "default": False
    }
}

CFG['gentoo'] = {
    "autotest_lang": {
        "default": "C, C++",
        "desc": "Language filter for ebuilds."
    },
    "autotest_use": {
        "default": "",
        "desc":
        "USE filter for ebuilds. Filters packages without the given use flags."
    },
    "autotest_loc": {
        "default": "/tmp/gentoo-autotest",
        "desc": "Location for the list of auto generated ebuilds."
    },
    "http_proxy": {
        "default": None,
        "desc": "HTTP Proxy to use for downloads."
    },
    "rsync_proxy": {
        "default": None,
        "desc": "RSYNC Proxy to use for downloads."
    },
    "ftp_proxy": {
        "default": None,
        "desc": "FTP Proxy to use for downloads."
    }
}

CFG["slurm"] = {
    "account": {
        "desc": "The SLURM account to use by default.",
        "default": "cl"
    },
    "partition": {
        "desc": "The SLURM partition to use by default.",
        "default": "chimaira"
    },
    "script": {
        "desc":
        "Name of the script that can be passed to SLURM. Used by external tools.",
        "default": "slurm.sh"
    },
    "cpus_per_task": {
        "desc":
        "Number of CPUs that should be requested from SLURM. Used by external tools.",
        "default": 10
    },
    "node_dir": {
        "desc":
        "Node directory, when executing on a cluster node. This is not "
        "used by pprof directly, but by external scripts.",
        "default": os.path.join(os.getcwd(), "results")
    },
    "timelimit": {
        "desc": "The timelimit we want to give to a job",
        "default": "12:00:00"
    },
    "exclusive": {
        "desc":
        "Shall we reserve a node exclusively, or share it with others?",
        "default": True
    },
    "multithread": {
        "desc": "Hint SLURM to allow multithreading. (--hint=nomultithread)",
        "default": False
    },
    "timelimit": {
        "desc": "Set a timelimit for the jobs.",
        "default": "12:00:00"
    },
    "logs": {
        "desc": "Location the SLURM logs will be stored",
        "default": "slurm.log"
    },
    "nice": {
        "desc": "Add a niceness value on our priority",
        "default": 0
    },
    "max_running": {
        "desc": "Limit the number of concurrent running array jobs",
        "default": 0
    }

}

CFG["perf"] = {
    "config" : {
        "default" : None,
        "desc" : "A configuration for the pollyperformance experiment."
    }
}


def find_config(default='.pprof.json', root=os.curdir):
    """
    Find the path to the default config file.

    We look at :root: for the :default: config file. If we can't find it
    there we start looking at the parent directory recursively until we
    find a file named :default: and return the absolute path to it.
    If we can't find anything, we return None.

    Args:
        default: The name of the config file we look for.
        root: The directory to start looking for.

    Returns:
        Path to the default config file, None if we can't find anything.
    """
    cur_path = os.path.join(root, default)
    if os.path.exists(cur_path):
        return cur_path
    else:
        new_root = os.path.abspath(os.path.join(root, os.pardir))
        return find_config(default, new_root) if new_root != root else None


def __init_config(cfg):
    """
    This will initialize the given configuration object.

    The following resources are available in the same order:
        1) Default settings.
        2) Config file.
        3) Environment variables.

    WARNING: Environment variables do _not_ take precedence over the config
             file right now. (init_from_env will refuse to update the
             value, if there is already one.)
    """
    config_path = find_config()
    if config_path:
        cfg.load(config_path)
        print("Configuration loaded from {}".format(os.path.abspath(
            config_path)))
    cfg.init_from_env()


__init_config(CFG)
