"""
Experiments module.

Experiments are discovered automatically by benchbuild.
You can configure the modules we search for experiments with the
settings:
    BB_PLUGINS_AUTOLOAD=True
    BB_PLUGINS_EXPERIMENTS=[...]

Any subclass of benchbuild.experiments.Experiment will be
automatically registered and made available on the command line.
"""
import importlib
import logging

from benchbuild.settings import CFG

LOG = logging.getLogger(__name__)


def discover():
    """Import all experiments listed in PLUGINS_EXPERIMENTS."""
    if CFG["plugins"]["autoload"]:
        experiment_plugins = CFG["plugins"]["experiments"].value
        for exp_plugin in experiment_plugins:
            try:
                importlib.import_module(exp_plugin)
            except ImportError as import_error:
                LOG.error("Could not find '%s'", exp_plugin)
                LOG.error("ImportError: %s", import_error.msg)
