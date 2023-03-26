"""
Support a light plugin infrastructure.

We dynamically load all modules listed in benchbuilds plugin configuration.
*_PLUGINS_{EXPERIMENTS,PROJECTS}. See benchbuild's default settings for more
details.

Autoloading of plugins requires the configuration option BB_PLUGINS_AUTOLOAD
to be set to True.

Any subclass of
    - benchbuild.experiment.Experiment
    - benchbuild.project.Project
will automatically register itself and is available on the CLI for all
subcommands.
"""
import importlib
import itertools
import logging

from benchbuild.settings import CFG

LOG = logging.getLogger(__name__)


def discover() -> bool:
    """Import all plugins listed in our configuration."""
    something_imported = False
    if CFG["plugins"]["autoload"]:
        experiment_plugins = CFG["plugins"]["experiments"].value
        project_plugins = CFG["plugins"]["projects"].value

        for plugin in itertools.chain(experiment_plugins, project_plugins):
            something_imported = True
            try:
                importlib.import_module(plugin)
            except ImportError as import_error:
                LOG.error("Could not find '%s'", import_error.name)
                LOG.debug("ImportError: %s", import_error)

    return something_imported
