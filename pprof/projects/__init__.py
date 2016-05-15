"""
Projects module.

By default, only projects that are listed in the configuration are
loaded automatically. See configuration variables:
 *_PLUGINS_AUTOLOAD
 *_PLUGINS_PROJECTS

"""
from pprof.settings import CFG
import logging
import importlib

def discover():
    if CFG["plugins"]["autoload"].value():
        log = logging.getLogger('pprof')
        project_plugins =  CFG["plugins"]["projects"].value()
        for pp in project_plugins:
            log.debug("Found project: {0}".format(pp))
            try:
                importlib.import_module(pp)
            except ImportError:
                log.error("Could not find '{0}'".format(pp))
