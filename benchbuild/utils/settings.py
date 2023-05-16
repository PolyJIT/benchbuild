"""
Configuration utilities.

Settings are stored in a dictionary-like configuration object.
All settings are modifiable by environment variables that encode
the path in the dictionary tree.

Inner nodes in the dictionary tree can be any dictionary.
A leaf node in the dictionary tree is represented by an inner node that
contains a value key.
"""
import copy
import logging
import os
import re
import sys
import typing as tp
import uuid
import warnings
from importlib.metadata import version, PackageNotFoundError

import attr
import schema
import six
import yaml
from plumbum import LocalPath, local

import benchbuild.utils.user_interface as ui

LOG = logging.getLogger(__name__)


class Indexable:

    def __getitem__(self: 'Indexable', key: str) -> 'Indexable':
        pass


try:
    __version__ = version("benchbuild")
except PackageNotFoundError:
    __version__ = "unknown"
    LOG.error("could not find version information.")


def available_cpu_count() -> int:
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
        match = re.search(
            r'(?m)^Cpus_allowed:\s*(.*)$',
            open('/proc/self/status').read()
        )
        if match:
            res = bin(int(match.group(1).replace(',', ''), 16)).count('1')
            if res > 0:
                return res
    except IOError:
        LOG.debug("Could not get the number of allowed CPUs")

    # http://code.google.com/p/psutil/
    try:
        import psutil
        return int(psutil.cpu_count())  # psutil.NUM_CPUS on old versions
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


def current_available_threads() -> int:
    """Returns the number of currently available threads for BB."""
    return len(os.sched_getaffinity(0))


def get_number_of_jobs(config: 'Configuration') -> int:
    """Returns the number of jobs set in the config."""
    jobs_configured = int(config["jobs"])
    if jobs_configured == 0:
        return current_available_threads()
    return jobs_configured


class InvalidConfigKey(RuntimeWarning):
    """Warn, if you access a non-existing key benchbuild's configuration."""


def escape_yaml(raw_str: str) -> str:
    """
    Shell-Escape a yaml input string.

    Args:
        raw_str: The unescaped string.
    """
    escape_list = [char for char in raw_str if char in ['!', '{', '[']]
    if len(escape_list) == 0:
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


def is_yaml(cfg_file: str) -> bool:
    """Is the given cfg_file a YAML file."""
    return os.path.splitext(cfg_file)[1] in [".yml", ".yaml"]


class ConfigLoader(yaml.CSafeLoader):  # type: ignore
    """Avoid polluting yaml's namespace with our modifications."""


class ConfigDumper(yaml.SafeDumper):
    """Avoid polluting yaml's namespace with our modifications."""


def to_yaml(value: tp.Any) -> tp.Optional[str]:
    """Convert a given value to a YAML string."""
    stream = yaml.io.StringIO()
    dumper = ConfigDumper(stream, default_flow_style=True, width=sys.maxsize)
    val = None
    try:
        dumper.open()
        dumper.represent(value)
        val = str(stream.getvalue()).strip()
        dumper.close()
    finally:
        dumper.dispose()

    return val


def to_env_var(env_var: str, value: tp.Any) -> str:
    """
    Create an environment variable from a name and a value.

    This generates a shell-compatible representation of an
    environment variable that is assigned a YAML representation of
    a value.

    Args:
        env_var (str): Name of the environment variable.
        value (Any): A value we convert from.
    """
    val = to_yaml(value)
    ret_val = "%s=%s" % (env_var, escape_yaml(str(val)))
    return ret_val


InnerNode = tp.Dict[str, tp.Any]

# This schema allows a configuration to be initialized/set from a standard
# dictionary. If you want to nest a new configuration node deeper than 1 level,
# you have to use dummy nodes to help benchbuild validate your nodes as
# Configuration nodes instead of plain dictionary values.
#
# Example:
#  CFG['container'] = {
#    'strategy': {
#      'dummy': { 'default': True, 'desc': 'Update portage tree' }
#    }
#  }
#  This opens the 'strategy' node up for deeper nesting in a second step:
#
#  CFG['container']['strategy']['polyjit'] = {
#    'sync': { 'default': True', 'desc': '...' }
#  }
_INNER_NODE_VALUE = schema.Schema({
    schema.Or('default', 'value'): object,
    schema.Optional('desc'): str
})
_INNER_NODE_SCHEMA = schema.Schema({
    schema.And(str, len): {
        schema.Or('default', 'value'): object,
        schema.Optional('desc'): str,
        schema.Optional(str): dict
    }
})


class Configuration(Indexable):
    """
    Dictionary-like data structure to contain all configuration variables.

    This serves as a configuration dictionary throughout benchbuild. You can
    use it to access all configuration options that are available. Whenever the
    structure is updated with a new subtree, all variables defined in the new
    subtree are updated from the environment.

    Environment variables are generated from the tree paths automatically.
        CFG["build_dir"] becomes BB_BUILD_DIR
        CFG["llvm"]["dir"] becomes BB_LLVM_DIR

    The configuration can be stored/loaded as YAML.
    """

    def __init__(
        self,
        parent_key: str,
        node: tp.Optional[InnerNode] = None,
        parent: tp.Optional['Configuration'] = None,
        init: bool = True
    ):
        self.parent = parent
        self.parent_key = parent_key
        self.node = node if node is not None else {}
        if init:
            self.init_from_env()

    def filter_exports(self) -> None:
        if self.has_default():
            do_export = True
            if "export" in self.node:
                do_export = self.node["export"]

            if not do_export:
                if self.parent:
                    self.parent.node.pop(self.parent_key)
        else:
            selfcopy = copy.deepcopy(self)
            for k in self.node:
                if selfcopy[k].is_leaf():
                    selfcopy[k].filter_exports()
            self.__dict__ = selfcopy.__dict__

    def store(self, config_file: LocalPath) -> None:
        """ Store the configuration dictionary to a file."""

        selfcopy = copy.deepcopy(self)
        selfcopy.filter_exports()

        with open(config_file, 'w') as outf:
            yaml.dump(
                selfcopy.node,
                outf,
                width=80,
                indent=4,
                default_flow_style=False,
                Dumper=ConfigDumper
            )

    def load(self, _from: LocalPath) -> None:
        """Load the configuration dictionary from file."""

        def load_rec(
            inode: tp.Dict[str, tp.Any], config: Configuration
        ) -> None:
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

        with open(str(_from), 'r') as infile:
            obj: Configuration = yaml.load(infile, Loader=ConfigLoader)
            upgrade(obj)
            load_rec(self.node, obj)
            self['config_file'] = os.path.abspath(_from)

    def has_value(self) -> bool:
        """Check, if the node contains a 'value'."""
        return isinstance(self.node, dict) and 'value' in self.node

    def has_default(self) -> bool:
        """Check, if the node contains a 'default' value."""
        return isinstance(self.node, dict) and 'default' in self.node

    def is_leaf(self) -> bool:
        """Check, if the node is a 'leaf' node."""
        return self.has_value() or self.has_default()

    def init_from_env(self) -> None:
        """
        Initialize this node from environment.

        If we're a leaf node, i.e., a node containing a dictionary that
        consist of a 'default' key, compute our env variable and initialize
        our value from the environment.
        Otherwise, init our children.
        """

        if 'default' in self.node:
            env_var = self.__to_env_var__().upper()
            if not self.has_value():
                self.node['value'] = self.node['default']
            env_val = os.getenv(env_var, None)
            if env_val is not None:
                try:
                    self.node['value'] = yaml.load(
                        str(env_val), Loader=ConfigLoader
                    )
                except ValueError:
                    self.node['value'] = env_val
        else:
            if isinstance(self.node, dict):
                for k in self.node:
                    self[k].init_from_env()

    @property
    def value(self) -> tp.Any:
        """Return the node value, if we're a leaf node."""

        def validate(node_value: tp.Any) -> tp.Any:
            if hasattr(node_value, 'validate'):
                node_value.validate()
            return node_value

        if 'value' in self.node:
            return validate(self.node['value'])
        return self

    def __getitem__(self, key: str) -> 'Configuration':
        if key not in self.node:
            warnings.warn(
                "Access to non-existing config element: {0}".format(key),
                category=InvalidConfigKey,
                stacklevel=2
            )
            return Configuration(key, init=False)
        return Configuration(key, parent=self, node=self.node[key], init=False)

    def __setitem__(self, key: str, val: tp.Any) -> None:
        if _INNER_NODE_SCHEMA.is_valid(val) or _INNER_NODE_VALUE.is_valid(val):
            self.node[key] = val
        elif key in self.node:
            self.node[key]['value'] = val
        else:
            self.node[key] = {'value': val}

    def __iadd__(self, rhs: tp.Any) -> tp.Any:
        """Append a value to a list value."""
        if not self.has_value():
            raise TypeError("Inner configuration node does not support +=.")

        value = self.node['value']
        if not hasattr(value, '__iadd__'):
            raise TypeError("Configuration node value does not support +=.")

        value += rhs
        return value

    def __int__(self) -> int:
        """Convert the node's value to int, if available."""
        if not self.has_value():
            raise ValueError(
                'Inner configuration nodes cannot be converted to int.'
            )
        return int(self.value)

    def __bool__(self) -> bool:
        """Convert the node's value to bool, if available."""
        if not self.has_value():
            return True
        return bool(self.value)

    def __contains__(self, key: str) -> bool:
        return key in self.node

    def __str__(self) -> str:
        if 'value' in self.node:
            return str(self.node['value'])
        return str(self.node)

    def __repr__(self) -> str:
        """
        Represents the configuration as a list of environment variables.
        """
        _repr = []

        if self.has_value():
            return to_env_var(self.__to_env_var__(), self.node['value'])
        if self.has_default():
            return to_env_var(self.__to_env_var__(), self.node['default'])

        for k in self.node:
            _repr.append(repr(self[k]))

        return "\n".join(sorted(_repr))

    def __to_env_var__(self) -> str:
        parent_key = self.parent_key
        if self.parent:
            return str(self.parent.__to_env_var__() + "_" + parent_key).upper()
        return parent_key.upper()

    def to_env_dict(self) -> tp.Mapping[str, tp.Any]:
        """Convert configuration object to a flat dictionary."""
        if self.has_value():
            return {self.__to_env_var__(): self.node['value']}
        if self.has_default():
            return {self.__to_env_var__(): self.node['default']}

        entries: tp.Dict[str, str] = {}
        for k in self.node:
            entries.update(self[k].to_env_dict())

        return entries


def convert_components(value: tp.Union[str, tp.List[str]]) -> tp.List[str]:
    is_str = isinstance(value, six.string_types)
    new_value = value
    if is_str:
        new_value = str(new_value)
        if os.path.sep in new_value:
            new_value = new_value.split(os.path.sep)
        else:
            new_value = [new_value]
    new_value = [c for c in new_value if c != '']
    return new_value


@attr.s(str=False, frozen=True)
class ConfigPath:
    """Wrapper around paths represented as list of strings."""
    components = attr.ib(converter=convert_components)

    def validate(self) -> None:
        """Make sure this configuration path exists."""
        path = local.path(ConfigPath.path_to_str(self.components))

        if not path.exists():
            print("The path '%s' is required by your configuration." % path)
            yes = ui.ask(
                "Should I create '%s' for you?" % path,
                default_answer=True,
                default_answer_str="yes"
            )
            if yes:
                path.mkdir()
            else:
                LOG.error("User denied path creation of '%s'.", path)
        if not path.exists():
            LOG.error("The path '%s' needs to exist.", path)

    @staticmethod
    def path_to_str(components: tp.List[str]) -> str:
        if components:
            return os.path.sep + os.path.sep.join(components)
        return os.path.sep

    def __str__(self) -> str:
        return ConfigPath.path_to_str(self.components)


def path_representer(dumper, data):
    """
    Represent a ConfigPath object as a scalar YAML node.
    """
    return dumper.represent_scalar('!create-if-needed', '%s' % data)


def path_constructor(loader, node):
    """"
    Construct a ConfigPath object form a scalar YAML node.
    """
    value = loader.construct_scalar(node)
    return ConfigPath(value)


def find_config(
    test_file: tp.Optional[str] = None,
    defaults: tp.Optional[tp.List[str]] = None,
    root: str = os.curdir
) -> tp.Optional[LocalPath]:
    """
    Find the path to the default config file.

    We look at :root: for the :default: config file. If we can't find it
    there we start looking at the parent directory recursively until we
    find a file named :default: and return the absolute path to it.
    If we can't find anything, we return None.

    Args:
        test_file:
        default: The name of the config file we look for.
        root: The directory to start looking for.

    Returns:
        Path to the default config file, None if we can't find anything.
    """
    if defaults is None:
        defaults = [".benchbuild.yml", ".benchbuild.yaml"]

    def walk_rec(cfg_name: str, root: str) -> LocalPath:
        cur_path = local.path(root) / cfg_name
        if cur_path.exists():
            return cur_path

        new_root = local.path(root) / os.pardir
        return walk_rec(cfg_name, new_root) if new_root != root else None

    if test_file is not None:
        return walk_rec(test_file, root)

    for test_f in defaults:
        ret = walk_rec(test_f, root)
        if ret is not None:
            return ret

    return None


def setup_config(
    cfg: Configuration,
    config_filenames: tp.Optional[tp.List[str]] = None,
    env_var_name: tp.Optional[str] = None
) -> None:
    """
    This will initialize the given configuration object.

    The following resources are available in the same order:
        1) Default settings.
        2) Config file.
        3) Environment variables.

    WARNING: Environment variables do _not_ take precedence over the config
             file right now. (init_from_env will refuse to update the
             value, if there is already one.)

    Args:
        config_filenames: list of possible config filenames
        env_var_name: name of the environment variable holding the config path
    """
    if env_var_name is None:
        env_var_name = "BB_CONFIG_FILE"

    config_path = os.getenv(env_var_name, None)
    if not config_path:
        config_path = find_config(defaults=config_filenames)

    if config_path:
        cfg.load(config_path)
        cfg["config_file"] = os.path.abspath(config_path)
    cfg.init_from_env()


def update_env(cfg: Configuration) -> None:
    env: tp.Dict[str, str] = dict(cfg["env"].value)

    path = env.get("PATH", "")
    path = os.path.pathsep.join(path)
    if "PATH" in os.environ:
        path = os.path.pathsep.join([path, os.environ["PATH"]])
    os.environ["PATH"] = path

    lib_path = env.get("LD_LIBRARY_PATH", "")
    lib_path = os.path.pathsep.join(lib_path)
    if "LD_LIBRARY_PATH" in os.environ:
        lib_path = os.path.pathsep.join([
            lib_path, os.environ["LD_LIBRARY_PATH"]
        ])
    os.environ["LD_LIBRARY_PATH"] = lib_path

    home = env.get("HOME", None)
    if home is not None and "HOME" in os.environ:
        os.environ["HOME"] = home

    # Update local's env property because we changed the environment
    # of the running python process.
    local.env.update(PATH=os.environ["PATH"])
    local.env.update(LD_LIBRARY_PATH=os.environ["LD_LIBRARY_PATH"])
    if home is not None:
        local.env.update(HOME=os.environ["HOME"])


def upgrade(cfg: Configuration) -> None:
    """Provide forward migration for configuration files."""
    db_node = cfg["db"]
    old_db_elems = ["host", "name", "port", "pass", "user", "dialect"]
    has_old_db_elems = [x in db_node for x in old_db_elems]

    if any(has_old_db_elems):
        print(
            "Old database configuration found. "
            "Converting to new connect_string. "
            "This will *not* be stored in the configuration automatically."
        )
        cfg["db"]["connect_string"] = \
            "{dialect}://{user}:{password}@{host}:{port}/{name}".format(
                dialect=cfg["db"]["dialect"]["value"],
                user=cfg["db"]["user"]["value"],
                password=cfg["db"]["pass"]["value"],
                host=cfg["db"]["host"]["value"],
                port=cfg["db"]["port"]["value"],
                name=cfg["db"]["name"]["value"])


def uuid_representer(dumper, data):
    """Represent a uuid.UUID object as a scalar YAML node."""

    return dumper.represent_scalar('!uuid', '%s' % data)


def uuid_constructor(loader, node):
    """"Construct a uuid.UUID object form a scalar YAML node."""

    value = loader.construct_scalar(node)
    return uuid.UUID(value)


def uuid_add_implicit_resolver(loader=ConfigLoader, dumper=ConfigDumper):
    """Attach an implicit pattern resolver for UUID objects."""
    uuid_regex = r'^\b[a-f0-9]{8}-\b[a-f0-9]{4}-\b[a-f0-9]{4}-\b[a-f0-9]{4}-\b[a-f0-9]{12}$'
    pattern = re.compile(uuid_regex)
    yaml.add_implicit_resolver('!uuid', pattern, Loader=loader, Dumper=dumper)


def __init_module__() -> None:
    yaml.add_representer(uuid.UUID, uuid_representer, Dumper=ConfigDumper)
    yaml.add_representer(ConfigPath, path_representer, Dumper=ConfigDumper)
    yaml.add_constructor('!uuid', uuid_constructor, Loader=ConfigLoader)
    yaml.add_constructor(
        '!create-if-needed', path_constructor, Loader=ConfigLoader
    )
    uuid_add_implicit_resolver()


__init_module__()
