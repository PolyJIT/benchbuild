"""
Configuration utilities.

Settings are stored in a dictionary-like configuration object.
All settings are modifiable by environment variables that encode
the path in the dictionary tree.

Inner nodes in the dictionary tree can be any dictionary.
A leaf node in the dictionary tree is represented by an inner node that contains a value key.
"""
import copy
import json
import logging
import os
import re
import uuid
import warnings

import yaml
from pkg_resources import DistributionNotFound, get_distribution
from plumbum import local

LOG = logging.getLogger(__name__)

try:
    __version__ = get_distribution("benchbuild").version
except DistributionNotFound:
    __version__ = "unknown"
    LOG.error("could not find version information.")


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
        LOG.debug("Could not get the number of allowed CPUs")

    # http://code.google.com/p/psutil/
    try:
        import psutil
        return psutil.cpu_count()  # psutil.NUM_CPUS on old versions
    except (ImportError, AttributeError):
        LOG.debug("Could not get the number of allowed CPUs")

    # POSIX
    try:
        res = int(os.sysconf('SC_NPROCESSORS_ONLN'))

        if res > 0:
            return res
    except (AttributeError, ValueError):
        LOG.debug("Could not get the number of allowed CPUs")

    # Linux
    try:
        res = open('/proc/cpuinfo').read().count('processor\t:')

        if res > 0:
            return res
    except IOError:
        LOG.debug("Could not get the number of allowed CPUs")

    raise Exception('Can not determine number of CPUs on this system')


class InvalidConfigKey(RuntimeWarning):
    """Warn, if you access a non-existing key benchbuild's configuration."""


class UUIDEncoder(json.JSONEncoder):
    """Encoder module for UUID objects."""

    def default(self, o):  # pylint: disable=E0202
        """Encode UUID objects as string."""
        if isinstance(o, uuid.UUID):
            return str(o)
        return json.JSONEncoder.default(self, o)


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


def is_yaml(cfg_file):
    return os.path.splitext(cfg_file)[1] in [".yml", ".yaml"]


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
        >>> from benchbuild.utils import settings as s
        >>> c = s.Configuration('bb')
        >>> c['test'] = 42
        >>> c['test']
        BB_TEST=42
        >>> str(c['test'])
        '42'
        >>> type(c['test'])
        <class 'benchbuild.utils.settings.Configuration'>
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
            self.__dict__ = selfcopy.__dict__

    def store(self, config_file):
        """ Store the configuration dictionary to a file."""

        selfcopy = copy.deepcopy(self)
        selfcopy.filter_exports()

        with open(config_file, 'w') as outf:
            if is_yaml(config_file):
                yaml.dump(
                    selfcopy.node,
                    outf,
                    width=80,
                    indent=4,
                    default_flow_style=False)
            else:
                json.dump(selfcopy.node, outf, cls=UUIDEncoder, indent=True)

    def load(self, _from):
        """Load the configuration dictionary from file."""

        def load_rec(inode, config):
            """Recursive part of loading."""
            for k in config:
                if isinstance(config[k], dict) and \
                   k not in ['value', 'default']:
                    if k in inode:
                        load_rec(inode[k], config[k])
                    else:
                        LOG.debug("+ config element: '%s'", k)
                else:
                    inode[k] = config[k]

        with open(_from, 'r') as infile:
            obj = yaml.load(infile) if is_yaml(_from) else json.load(infile)
            upgrade(obj)
            load_rec(self.node, obj)
            self['config_file'] = os.path.abspath(_from)

    def has_value(self):
        """Check, if the node contains a 'value'."""
        return isinstance(self.node, dict) and 'value' in self.node

    def has_default(self):
        """Check, if the node contains a 'default' value."""
        return isinstance(self.node, dict) and 'default' in self.node

    def is_leaf(self):
        """Check, if the node is a 'leaf' node."""
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
            >>> from benchbuild.utils import settings as s
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
            warnings.warn(
                "Tried to get the str() value of an inner node.", stacklevel=2)
            return str(self.node)

    def __repr__(self):
        _repr = []
        if self.has_value():
            return self.__to_env_var__() + "=" + escape_json(
                json.dumps(self.node['value'], cls=UUIDEncoder))
        if self.has_default():
            return self.__to_env_var__() + "=" + escape_json(
                json.dumps(self.node['default'], cls=UUIDEncoder))

        for k in self.node:
            _repr.append(repr(self[k]))

        return "\n".join(sorted(_repr))

    def __to_env_var__(self):
        parent_key = self.parent_key
        if self.parent:
            return (self.parent.__to_env_var__() + "_" + parent_key).upper()
        return parent_key.upper()

    def to_env_dict(self):
        """Convert configuration object to a flat dictionary."""
        entries = {}
        if self.has_value():
            return {self.__to_env_var__(): self.node['value']}
        if self.has_default():
            return {self.__to_env_var__(): self.node['default']}

        for k in self.node:
            entries.update(self[k].to_env_dict())

        return entries


def __find_config__(test_file=None, defaults=None, root=os.curdir):
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
    if defaults is None:
        defaults = [".benchbuild.yml", ".benchbuild.yaml", ".benchbuild.json"]

    def walk_rec(cur_path, root):
        cur_path = os.path.join(root, test_file)
        if os.path.exists(cur_path):
            return cur_path
        else:
            new_root = os.path.abspath(os.path.join(root, os.pardir))
            return walk_rec(cur_path, new_root) if new_root != root else None

    if test_file is not None:
        return walk_rec(test_file, root)
    else:
        for test_file in defaults:
            ret = walk_rec(test_file, root)
            if ret is not None:
                return ret


def setup_config(cfg):
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
        config_path = __find_config__()

    if config_path:
        cfg.load(config_path)
        cfg["config_file"] = os.path.abspath(config_path)
    cfg.init_from_env()


def update_env(cfg):
    path = cfg["env"]["path"].value()
    path = os.path.pathsep.join(path)
    if "PATH" in os.environ:
        path = os.path.pathsep.join([path, os.environ["PATH"]])
    os.environ["PATH"] = path

    lib_path = cfg["env"]["ld_library_path"].value()
    lib_path = os.path.pathsep.join(lib_path)
    if "LD_LIBRARY_PATH" in os.environ:
        lib_path = os.path.pathsep.join(
            [lib_path, os.environ["LD_LIBRARY_PATH"]])
    os.environ["LD_LIBRARY_PATH"] = lib_path

    # Update local's env property because we changed the environment
    # of the running python process.
    local.env.update(PATH=os.environ["PATH"])
    local.env.update(LD_LIBRARY_PATH=os.environ["LD_LIBRARY_PATH"])


def upgrade(cfg):
    """Provide forward migration for configuration files."""
    db_node = cfg["db"]
    old_db_elems = ["host", "name", "port", "pass", "user", "dialect"]
    has_old_db_elems = [x in db_node for x in old_db_elems]

    if any(has_old_db_elems):
        print("Old database configuration found. "
              "Converting to new connect_string. "
              "This will *not* be stored in the configuration automatically.")
        cfg["db"]["connect_string"] = \
            "{dialect}://{user}:{password}@{host}:{port}/{name}".format(
                dialect=cfg["db"]["dialect"]["value"],
                user=cfg["db"]["user"]["value"],
                password=cfg["db"]["pass"]["value"],
                host=cfg["db"]["host"]["value"],
                port=cfg["db"]["port"]["value"],
                name=cfg["db"]["name"]["value"])
