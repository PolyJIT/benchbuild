"""
Module support for benchbuild.

We provide a new module API for benchbuild. This allows for projects/experiments and extensions to live in a completly separate repository, reducing benchbuild's test surface.
A module is essentially a folder containing a single file: .benchbuild-module.yml
The format of the .yml is as follows:

Example .benchbuild-module.yml
```yaml
modules:
    - name: bzip2
      main: benchbuild.projects.bzip2
      settings: {}
```

The top-level element may contain a list of descriptors.
Each descriptor element must contain a dict with at least the following entries:
    name: <str> - The name of the plugin
    main: <str> - The name of 
In addition, you may provide an additional settings dict behind the
'settings' key. This structure must follow benchbuild's configuration data
structure and will be hooked into the default configuration at:
```
    CFG[<(projects|experiments|extensions)>][<name>]
```

All modules that should be included by benchbuild have to be added to the
configuration at:
```
    CFG['plugins']['modules']
```
Each entry has to suffice the following format ``"<name>": "<path>"``
Where <path> is a git repository, or an absolute path to a directory.
"""
import logging
from typing import Dict, List, Tuple

import attr
import yaml
from plumbum import local
from plumbum.path.local import LocalPath

from benchbuild.settings import CFG
from benchbuild.utils.cmd import git
from benchbuild.utils.settings import Configuration

LOG = logging.getLogger(__name__)
__MODULE_CONFIG__: str = '.benchbuild-module.yml'

@attr.s()
class Module:
    name: str = attr.ib()
    main: str = attr.ib()
    settings: Configuration = attr.ib()


def __create_modules__(module_config: str) -> List[Module]:
    config = local.path(module_config)
    if not (config.exists() or config.is_dir()):
        LOG.error('Path "%s" does not exist', module_config)
        return []

    with open(config, 'r') as hdl:
        loaded = yaml.safe_load(hdl)

    LOG.debug("YAML in config: %s", repr(loaded))
    assert 'modules' in loaded
    mods = []
    for mod in loaded['modules']:
        assert 'name' in mod
        assert 'main' in mod
        _name = mod['name']
        _main = mod['main']
        _settings = mod['settings'] if 'settings' in mod else {}
        mods.append(Module(_name, _main, Configuration('bb', node=_settings)))
    return mods

def __download__(name: str, source: str) -> str:
    LOG.debug('Check, if we need to download: "%s"', name)
    prefix = local.path(str(CFG['environment']))
    def __exists__(mod_path: LocalPath) -> bool:
        if mod_path.exists() and mod_path.is_dir():
            LOG.debug('Module "%s" found in environment "%s"', name, mod_path)
            return True
        LOG.debug('Module "%s" not found in environment "%s"', name, mod_path)
        return False

    def __updated__(mod_path: LocalPath) -> bool:
        git_dir = mod_path / ".git"
        if __exists__(git_dir):
            with local.cwd(mod_path):
                git("reset", "--hard", "HEAD")
                git("pull")

    path = prefix / source
    for path in [prefix / source, prefix / name]:
        if __exists__(path):
            if __updated__(path):
                LOG.info("Repository was updated: %s", path)
            return path / __MODULE_CONFIG__

    LOG.debug('Downloading "%s" from: "%s"', name, source)
    git("clone", source, path)
    return path / __MODULE_CONFIG__


def create_modules(modules: Dict[str, str]) -> List[Module]:
    modules_to_load = []
    for name, source in modules.items():
        mod_location = __download__(name, source)
        mods = __create_modules__(mod_location)
        LOG.debug("Loaded module: %s", str(mods))
        modules_to_load.extend(mods)
    return modules_to_load

def load_modules(modules: List[Module]):
    ...
