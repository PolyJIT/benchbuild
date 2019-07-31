"""
Module support for benchbuild.

We provide a new module API for benchbuild. This allows for projects/experiments
and extensions to live in a completly separate repository, reducing benchbuild's
test surface. A module is essentially a folder containing a single file:
    .benchbuild-module.yml
The format is as follows:

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
import importlib.util
import logging
import sys
from typing import Dict, List

import attr
import pygit2
import yaml
from plumbum import local
from plumbum.path.local import LocalPath

from benchbuild.settings import CFG
from benchbuild.utils.settings import Configuration

LOG = logging.getLogger(__name__)
__MODULE_PREFIX__: str = 'benchbuild.module.'
__MODULE_CONFIG__: str = '.benchbuild-module.yml'


@attr.s()
class Module:
    name: str = attr.ib()
    main: str = attr.ib()
    settings: Configuration = attr.ib()
    prefix: LocalPath = attr.ib()


def create_modules(modules: Dict[str, str]) -> List[Module]:
    modules_to_load = []
    for name, source in modules.items():
        mod_location = __download__(name, source)
        mods = __create_modules__(mod_location)
        modules_to_load.extend(mods)
    return modules_to_load


def init_environment(modules: List[Module]):
    """
    Initialize the environment.

    Args:
        modules: List of module wrappers.
    """
    loaded = []
    for module in modules:
        mod_spec = importlib.util.spec_from_file_location(
            str(__MODULE_PREFIX__ + module.name), str(module.prefix / module.main))
        mod = importlib.util.module_from_spec(mod_spec)
        if mod:
            if mod_spec.loader:
                mod_spec.loader.exec_module(mod)
                loaded.append(mod)
                sys.modules[__MODULE_PREFIX__ + module.name] = mod
                LOG.debug("Loaded module: %s", mod.__name__)
    return loaded


def init():
    """Discover and load all modules into an environment."""
    init_environment(create_modules(CFG['plugins']['modules'].value))


def __create_modules__(module_config: LocalPath) -> List[Module]:
    if not (module_config.exists() or module_config.is_dir()):
        LOG.error('Path "%s" does not exist', module_config)
        return []

    with open(module_config, 'r') as hdl:
        loaded = yaml.safe_load(hdl)

    assert 'modules' in loaded
    mods = []
    for mod in loaded['modules']:
        assert 'name' in mod
        assert 'main' in mod
        _name = mod['name']
        _main = mod['main']
        _settings = mod['settings'] if 'settings' in mod else {}
        mods.append(
            Module(_name, _main, Configuration('bb', node=_settings),
                   module_config.dirname))
    return mods


def __git_pull__(mod_path: LocalPath) -> bool:
    repo_path: str = pygit2.discover_repository(mod_path, 0, mod_path)
    if repo_path:
        LOG.debug("Repository found at: %s", repo_path)
        repo = pygit2.Repository(repo_path)
        repo.reset(repo.head.target, pygit2.GIT_RESET_HARD)
        remote: pygit2.Remote = repo.remotes['origin']
        remote.fetch()

        remote_master_id = repo.lookup_reference(
            'refs/remotes/origin/master').target
        merge_result, _ = repo.merge_analysis(remote_master_id)
        # Up to date, do nothing
        if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
            return False
        # We can just fastforward
        elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
            repo.checkout_tree(repo.get(remote_master_id))
            master_ref = repo.lookup_reference('refs/heads/master')
            master_ref.set_target(remote_master_id)
            repo.head.set_target(remote_master_id)
        elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
            repo.merge(remote_master_id)
            LOG.error(repo.index.conflicts)

            assert repo.index.conflicts is None, 'Conflicts, ahhhh!'
            user = repo.default_signature
            tree = repo.index.write_tree()
            repo.create_commit('HEAD', user, user, 'Merge!', tree,
                               [repo.head.target, remote_master_id])
            repo.state_cleanup()
        else:
            raise AssertionError('Unknown merge analysis result')
        return True
    return False


def __download__(name: str, source: str) -> str:
    LOG.debug('Check, if we need to download: "%s"', name)
    prefix = local.path(str(CFG['environment']))

    def __exists__(mod_path: LocalPath) -> bool:
        if mod_path.exists() and mod_path.is_dir():
            return True
        return False

    def __updated__(mod_path: LocalPath) -> bool:
        __git_pull__(mod_path)
        return True

    path = prefix / source
    for path in [prefix / source, prefix / name]:
        if __exists__(path):
            if __updated__(path):
                LOG.info("Repository was updated: %s", path)
            return path / __MODULE_CONFIG__

    LOG.debug('Downloading "%s" from: "%s"', name, source)
    pygit2.clone_repository(source, path)
    return path / __MODULE_CONFIG__
