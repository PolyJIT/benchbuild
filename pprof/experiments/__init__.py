"""
Experiments module.

By default, only experiments that are listed in the configuration are
loaded automatically. See configuration variables:
 *_PLUGINS_AUTOLOAD
 *_PLUGINS_EXPERIMENTS

"""
from pprof.settings import CFG
import logging
import importlib

def discover():
    """
    Import all experiments listed in PLUGINS_EXPERIMENTS.

    Tests:
        >>> from pprof.settings import CFG
        >>> from pprof.experiments import discover
        >>> import logging as lg
        >>> import sys
        >>> l = lg.getLogger('pprof')
        >>> lg.getLogger('pprof').setLevel(lg.DEBUG)
        >>> lg.getLogger('pprof').handlers = [lg.StreamHandler(stream=sys.stdout)]
        >>> CFG["plugins"]["experiments"] = ["pprof.non.existing", "pprof.experiments.raw"]
        >>> discover()
        Could not find 'pprof.non.existing'
        Found experiment: pprof.experiments.raw
    """
    if CFG["plugins"]["autoload"].value():
        log = logging.getLogger('pprof')
        experiment_plugins = CFG["plugins"]["experiments"].value()
        for ep in experiment_plugins:
            try:
                importlib.import_module(ep)
                log.debug("Found experiment: {0}".format(ep))
            except ImportError:
                log.error("Could not find '{0}'".format(ep))
