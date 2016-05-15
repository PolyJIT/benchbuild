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
    if CFG["plugins"]["autoload"].value():
        log = logging.getLogger('pprof')
        experiment_plugins =  CFG["plugins"]["experiments"].value()
        for ep in experiment_plugins:
            log.debug("Found experiment: {0}".format(ep))
            importlib.import_module(ep)
