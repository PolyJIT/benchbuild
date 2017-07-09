"""
Experiments module.

By default, only experiments that are listed in the configuration are
loaded automatically. See configuration variables:
 *_PLUGINS_AUTOLOAD
 *_PLUGINS_EXPERIMENTS

"""
from benchbuild.settings import CFG
import logging
import importlib

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
        Found experiment: benchbuild.experiments.raw
    """
    if CFG["plugins"]["autoload"].value():
        experiment_plugins = CFG["plugins"]["experiments"].value()
        for ep in experiment_plugins:
            try:
                importlib.import_module(ep)
                LOG.debug("Found experiment: %s", ep)
            except ImportError as ie:
                LOG.error("Could not find '%s'", ep)
                LOG.error("ImportError: %s", ie.msg)
