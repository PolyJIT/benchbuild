"""
Settings module for benchbuild.

All settings are stored in a simple dictionary. Each
setting should be modifiable via environment variable.
"""
import json
import os
import uuid
import re
import warnings
import logging
import copy
from datetime import datetime
from plumbum import local


def available_cpu_count():
    """
    Get the number of available CPUs.

    Number of available virtual or physical CPUs on this system, i.e.
    user/real as output by time(1) when called with an optimally scaling
    userspace-only program.

    Returns:
        Number of avaialable CPUs.
    """
    log = logging.getLogger('benchbuild')

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
        log.debug("Could not get the number of allowed CPUs")

    # http://code.google.com/p/psutil/
    try:
        import psutil
        return psutil.cpu_count()  # psutil.NUM_CPUS on old versions
    except (ImportError, AttributeError):
        log.debug("Could not get the number of allowed CPUs")

    # POSIX
    try:
        res = int(os.sysconf('SC_NPROCESSORS_ONLN'))

        if res > 0:
            return res
    except (AttributeError, ValueError):
        log.debug("Could not get the number of allowed CPUs")

    # Linux
    try:
        res = open('/proc/cpuinfo').read().count('processor\t:')

        if res > 0:
            return res
    except IOError:
        log.debug("Could not get the number of allowed CPUs")

    raise Exception('Can not determine number of CPUs on this system')


class InvalidConfigKey(RuntimeWarning):
    """Warn, if you access a non-existing key benchbuild's configuration."""


class UUIDEncoder(json.JSONEncoder):
    """Encoder module for UUID objects."""

    def default(self, obj):
        """Encode UUID objects as string."""
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def escape_json(raw_str):
    """
    Shell-Escape a json input string.

    Args:
        raw_str: The unescaped string.
    """
    json_list = '['
    json_set = '{'
    if json_list not in raw_str and json_set not in raw_str:
        return raw_str

    str_quotes = '"'
    i_str_quotes = "'"
    if str_quotes in raw_str and str_quotes not in raw_str[1:-1]:
        return raw_str

    if str_quotes in raw_str[1:-1]:
        raw_str = i_str_quotes + raw_str + i_str_quotes
    else:
        raw_str = str_quotes + raw_str + str_quotes
    return raw_str


class Configuration():
    """
    Dictionary-like data structure to contain all configuration variables.

    This serves as a configuration dictionary throughout benchbuild. You can
    use it to access all configuration options that are available. Whenever the
    structure is updated with a new subtree, all variables defined in the new
    subtree are updated from the environment.

    Environment variables are generated from the tree paths automatically.
        CFG["build_dir"] becomes BB_BUILD_DIR
        CFG["llvm"]["dir"] becomes BB_LLVM_DIR

    The configuration can be stored/loaded as JSON.

    Examples:
        >>> from benchbuild import settings as s
        >>> c = s.Configuration('bb')
        >>> c['test'] = 42
        >>> c['test']
        BB_TEST=42
        >>> str(c['test'])
        '42'
        >>> type(c['test'])
        <class 'benchbuild.settings.Configuration'>
    """

    def __init__(self, parent_key, node=None, parent=None, init=True):
        self.parent = parent
        self.parent_key = parent_key
        self.node = node if node is not None else {}
        if init:
            self.init_from_env()

    def filter_exports(self):
        if self.has_default():
            do_export = True
            if "export" in self.node:
                do_export = self.node["export"]

            if not do_export:
                self.parent.node.pop(self.parent_key)
        else:
            selfcopy = copy.deepcopy(self)
            for k in self.node:
                if selfcopy[k].is_leaf():
                    selfcopy[k].filter_exports()
            self = selfcopy

    def store(self, config_file):
        """ Store the configuration dictionary to a file."""

        selfcopy = copy.deepcopy(self)
        selfcopy.filter_exports()

        with open(config_file, 'w') as outf:
            json.dump(selfcopy.node, outf, cls=UUIDEncoder, indent=True)

    def load(self, _from):
        """Load the configuration dictionary from file."""

        def load_rec(inode, config):
            for k in config:
                if isinstance(config[k], dict):
                    if k in inode:
                        load_rec(inode[k], config[k])
                    else:
                        log = logging.getLogger('benchbuild')
                        log.warn(warnings.formatwarning(
                            "Key {} is not part of the default config, "
                            "ignoring.".format(k),
                            category=InvalidConfigKey, filename=str(__file__),
                            lineno=180))
                else:
                    inode[k] = config[k]

        if os.path.exists(_from):
            with open(_from, 'r') as inf:
                load_rec(self.node, json.load(inf))
                self['config_file'] = os.path.abspath(_from)

    def has_value(self):
        return isinstance(self.node, dict) and 'value' in self.node

    def has_default(self):
        return isinstance(self.node, dict) and 'default' in self.node

    def is_leaf(self):
        return self.has_value() or self.has_default()

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
            if self.has_value():
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
            >>> from benchbuild import settings as s
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
        if key not in self.node:
            warnings.warn(
                "Access to non-existing config element: {0}".format(key),
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
        if self.has_value():
            return self.__to_env_var__() + "=" + escape_json(json.dumps(
                self.node['value']))
        if self.has_default():
            return self.__to_env_var__() + "=" + escape_json(json.dumps(
                self.node['default']))

        for k in self.node:
            _repr.append(repr(self[k]))

        return "\n".join(sorted(_repr))

    def __to_env_var__(self):
        if self.parent:
            return (
                self.parent.__to_env_var__() + "_" + self.parent_key).upper()
        return self.parent_key.upper()


def to_env_dict(config):
    """Convert configuration object to a flat dictionary."""
    entries = {}
    if config.has_value():
        return {config.__to_env_var__(): config.node['value']}
    if config.has_default():
        return {config.__to_env_var__(): config.node['default']}

    for k in config.node:
        entries.update(to_env_dict(config[k]))

    return entries


# Initialize the global configuration once.
CFG = Configuration(
    "bb",
    node={
        "version": {
            "desc": "Version Number",
            "default": "1.2.1"
        },
        "verbosity": {
            "desc": "The verbosity level of the logger. Range: 0-4",
            "default": 0
        },
        "config_file": {
            "desc": "Config file path of benchbuild. Not guaranteed to exist.",
            "default": None,
        },
        "src_dir": {
            "desc":
            "source directory of benchbuild. Usually the git repo root dir.",
            "default": os.getcwd()
        },
        "build_dir": {
            "desc":
            "build directory of benchbuild. All intermediate projects will "
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
            "desc": "Additional PATH variable for benchbuild.",
            "default": ""
        },
        "ld_library_path": {
            "desc": "Additional library path for benchbuild.",
            "default": ""
        },
        "jobs": {
            "desc":
            "Number of jobs that can be used for building and running.",
            "default": str(available_cpu_count())
        },
        "experiment_id": {
            "desc":
            "The experiment UUID we run everything under."
            "This groups the project runs in the database.",
            "default": str(uuid.uuid4()),
            "export": False
        },
        "experiment": {
            "desc": "The experiment name we run everything under.",
            "default": "empty"
        },
        "clean": {
            "default": True,
            "desc": "Clean temporary objects, after completion.",
        },
        "experiment_description": {
            "default": str(datetime.now()),
            "export": False
        },
        "regression_prefix": {
            "default": os.path.join("/", "tmp", "benchbuild-regressions")
        },
        "benchbuild_prefix": {
            "default": os.getcwd()
        },
        "benchbuild_ebuild": {
            "default": ""
        },
        "cleanup_paths": {
            "default": [],
            "desc":
            "List of existing paths that benchbuild should delete in addition "
            "to the default cleanup steps."
        },
        "use_database": {
            "desc": "LEGACY: Store results from libpprof in the database.",
            "default": 1
        }
    })

CFG["unionfs"] = {
    "enable": {
        "default": True,
        "desc": "Wrap all project operations in a unionfs filesystem."
    },
    "base_dir": {
        "default": './base',
        "desc": 'Path of the unpacked container.'
    },
    "image": {
        "default": './image',
        "desc": 'Name of the image directory'
    },
    "image_prefix": {
        "default": None,
        "desc": "Prefix for the unionfs image directory."
    }
}

CFG["env"] = {
    "compiler_ld_library_path": {
        "desc":
        "List of paths to be added to the LD_LIBRARY_PATH variable of all "
        "compiler invocations.",
        "default": []
    },
    "compiler_path": {
        "desc":
        "List of paths to be added to all PATH variable of all compiler "
        "invocations.",
        "default": []
    },
    "binary_ld_library_path": {
        "desc":
        "List of paths to be added to the LD_LIBRARY_PATH variable of all "
        "binary invocations.",
        "default": []
    },
    "binary_path": {
        "desc":
        "List of paths to be added to the PATH variable of all binary"
        "invocations.",
        "default": []
    },
    "lookup_path": {
        "desc": "Search path for plumbum imports",
        "default": []
    },
    "lookup_ld_library_path": {
        "desc": "LD_LIBRARY_PATH for plumbum imports",
        "default": []
    }
}

CFG["llvm"] = {
    "dir": {
        "desc": "Path to LLVM. This will be required.",
        "default": os.path.join(os.getcwd(), "install")
    },
    "src": {
        "default": os.path.join(os.getcwd(), "benchbuild-llvm")
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
        "default": "benchbuild"
    },
    "user": {
        "desc":
        "The name of the PostgreSQL user to connect to the database with.",
        "default": "benchbuild"
    },
    "pass": {
        "desc":
        "The password for the PostgreSQL user used to connect to the database "
        "with.",
        "default": "benchbuild"
    },
    "rollback": {
        "desc": "Rollback all operations after benchbuild completes.",
        "default": False
    }
}

CFG['gentoo'] = {
    "autotest_lang": {
        "default": "",
        "desc": "Language filter for ebuilds, like C or C++."
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
        "Name of the script that can be passed to SLURM. Used by external "
        "tools.",
        "default": "slurm.sh"
    },
    "cpus_per_task": {
        "desc":
        "Number of CPUs that should be requested from SLURM. Used by external "
        "tools.",
        "default": 10
    },
    "node_dir": {
        "desc":
        "Node directory, when executing on a cluster node. This is not "
        "used by benchbuild directly, but by external scripts.",
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
    "turbo": {
        "desc": "Disable Intel Turbo Boost via SLURM. (--pstate-turbo=off)",
        "default": False
    },
    "logs": {
        "desc": "Location the SLURM logs will be stored",
        "default": "slurm.log"
    },
    "nice": {
        "desc": "Add a niceness value on our priority",
        "default": 0
    },
    "nice_clean": {
        "desc": "Add a niceness value on our cleanup job priority",
        "default": 2500
    },
    "max_running": {
        "desc": "Limit the number of concurrent running array jobs",
        "default": 0
    },
    "node_image": {
        "desc": "Path to the archive we want on each cluster node.",
        "default": os.path.join(os.path.curdir, "llvm.tar.gz")
    },
    "extra_log": {
        "desc": "Extra log file to be managed by SLURM",
        "default": "/tmp/.slurm"
    }
}

CFG["perf"] = {
    "config": {
        "default": None,
        "desc": "A configuration for the pollyperformance experiment."
    }
}

CFG["cs"] = {
    "components": {
        "default": None,
        "desc": "List of filters for compilestats components."
    },
    "names": {
        "default": None,
        "desc": "List of filters for compilestats names."
    }
}

CFG["uchroot"] = {
    "repo": {
        "default": "https://github.com/PolyJIT/erlent.git/",
        "desc": "GIT Repo URL for erlent."
    },
    "mounts": {
        "default": [],
        "desc": "Mount points that should be available inside uchroot."
    }
}

CFG["plugins"] = {
    "autoload": {
        "default": True,
        "desc": "Should automatic load of plugins be enabled?"
    },
    "reports": {
        "default": [
            "benchbuild.reports.raw"
        ],
        "desc": "Report plugins."
    },
    "experiments": {
        "default": [
            "benchbuild.experiments.raw",
            "benchbuild.experiments.compilestats",
            "benchbuild.experiments.polyjit",
            "benchbuild.experiments.empty",
            "benchbuild.experiments.papi",
            "benchbuild.experiments.compilestats_ewpt",
        ],
        "desc": "The experiment plugins we know about."
    },
    "projects": {
        "default": [
            "benchbuild.projects.gentoo",
            "benchbuild.projects.lnt.lnt",
            "benchbuild.projects.polybench.polybench",
            "benchbuild.projects.benchbuild.bzip2",
            "benchbuild.projects.benchbuild.ccrypt",
            "benchbuild.projects.benchbuild.crafty",
            "benchbuild.projects.benchbuild.crocopat",
            "benchbuild.projects.benchbuild.ffmpeg",
            "benchbuild.projects.benchbuild.gzip",
            "benchbuild.projects.benchbuild.js",
            "benchbuild.projects.benchbuild.lammps",
            "benchbuild.projects.benchbuild.lapack",
            "benchbuild.projects.benchbuild.leveldb",
            "benchbuild.projects.benchbuild.linpack",
            "benchbuild.projects.benchbuild.lulesh",
            "benchbuild.projects.benchbuild.luleshomp",
            "benchbuild.projects.benchbuild.mcrypt",
            "benchbuild.projects.benchbuild.minisat",
            "benchbuild.projects.benchbuild.openssl",
            "benchbuild.projects.benchbuild.postgres",
            "benchbuild.projects.benchbuild.povray",
            "benchbuild.projects.benchbuild.python",
            "benchbuild.projects.benchbuild.rasdaman",
            "benchbuild.projects.benchbuild.ruby",
            "benchbuild.projects.benchbuild.sdcc",
            "benchbuild.projects.benchbuild.sevenz",
            "benchbuild.projects.benchbuild.sqlite3",
            "benchbuild.projects.benchbuild.tcc",
            "benchbuild.projects.benchbuild.x264",
            "benchbuild.projects.benchbuild.xz",
            "benchbuild.projects.apollo.scimark",
            "benchbuild.projects.apollo.rodinia"
        ],
        "desc": "The project plugins we know about."
    }
}

CFG["container"] = {
    "input": {
        "default": "container.tar.bz2",
        "desc": "Input container file/folder."
    },
    "output": {
        "default": "container-out.tar.bz2",
        "desc": "Output container file."
    },
    "mounts": {
        "default": [],
        "desc": "List of paths that will be mounted inside the container."
    },
    "shell": {
        "default": "/bin/bash",
        "desc": "Command string that should be used as shell command."
    },
    "known": {
        "default": [],
        "desc": "List of known containers. Format: "
                "[{ 'path': <path>,"
                "   'hash': <hash> }]"
    },
    "prefered": {
        "default": [],
        "desc": "List of containers of which the project can chose from."
                "Format:"
                "[{ 'path': <path> }]"
    },
    "strategy": {
        "polyjit": {
            "packages": {
                "default": [
                    {"name": "dev-db/postgresql", "use": []},
                    {"name": "net-misc/curl", "use": []},
                    {"name": "likwid", "use": ["-filecaps"]},
                    {"name": "dev-libs/libpfm", "use": ["static-libs"]},
                    {"name": "sys-process/time", "use": []},
                    {"name": "dev-utils/boost-build", "use": []},
                    {"name": "dev-libs/boost", "use": []},
                ],
                "desc": "A list of gentoo package atoms that should be merged."
            }
        }
    }
}


def find_config(default='.benchbuild.json', root=os.curdir):
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
    config_path = os.getenv("BB_CONFIG_FILE", None)
    if not config_path:
        config_path = find_config()

    if config_path:
        cfg.load(config_path)
        cfg["config_file"] = os.path.abspath(config_path)
        logging.debug("Configuration loaded from {0}".format(os.path.abspath(
            config_path)))
    cfg.init_from_env()


def update_env():
    lookup_path = CFG["env"]["lookup_path"].value()
    lookup_path = os.path.pathsep.join(lookup_path)
    if "PATH" in os.environ:
        lookup_path = os.path.pathsep.join([lookup_path, os.environ["PATH"]])
    os.environ["PATH"] = lookup_path

    lib_path = CFG["env"]["lookup_ld_library_path"].value()
    lib_path = os.path.pathsep.join(lib_path)
    if "LD_LIBRARY_PATH" in os.environ:
        lib_path = os.path.pathsep.join([lib_path,
                                        os.environ["LD_LIBRARY_PATH"]])
    os.environ["LD_LIBRARY_PATH"] = lib_path

    # Update local's env property because we changed the environment
    # of the running python process.
    local.env.update(PATH=os.environ["PATH"])
    local.env.update(LD_LIBRARY_PATH=os.environ["LD_LIBRARY_PATH"])


__init_config(CFG)
