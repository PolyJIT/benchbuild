"""
Experiments module.

By default, only experiments that are listed in the configuration are
loaded automatically. See configuration variables:
 *_PLUGINS_AUTOLOAD
 *_PLUGINS_EXPERIMENTS

"""
import logging
import importlib

from benchbuild.settings import CFG

LOG = logging.getLogger(__name__)


def discover():
    """
    Import all experiments listed in PLUGINS_EXPERIMENTS.

    Tests:
        >>> from benchbuild.settings import CFG
        >>> from benchbuild.experiments import discover
        >>> import logging as lg
        >>> import sys
        >>> l = lg.getLogger('benchbuild')
        >>> lg.getLogger('benchbuild').setLevel(lg.DEBUG)
        >>> lg.getLogger('benchbuild').handlers = [lg.StreamHandler(stream=sys.stdout)]
        >>> CFG["plugins"]["experiments"] = ["benchbuild.non.existing", "benchbuild.experiments.raw"]
        >>> discover()
        Could not find 'benchbuild.non.existing'
        ImportError: No module named 'benchbuild.non'
    """
    if CFG["plugins"]["autoload"].value():
        experiment_plugins = CFG["plugins"]["experiments"].value()
        for exp_plugin in experiment_plugins:
            try:
                importlib.import_module(exp_plugin)
            except ImportError as import_error:
                LOG.error("Could not find '%s'", exp_plugin)
                LOG.error("ImportError: %s", import_error.msg)
