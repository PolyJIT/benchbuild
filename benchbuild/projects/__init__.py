"""
Projects module.

By default, only projects that are listed in the configuration are
loaded automatically. See configuration variables:
 *_PLUGINS_AUTOLOAD
 *_PLUGINS_PROJECTS

"""
import logging
import importlib

from benchbuild.settings import CFG

LOG = logging.getLogger(__name__)


def discover():
    if CFG["plugins"]["autoload"].value():
        project_plugins = CFG["plugins"]["projects"].value()
        for project_plugin in project_plugins:
            try:
                importlib.import_module(project_plugin)
            except ImportError as import_error:
                LOG.error("Could not find '%s'", project_plugin)
                LOG.error("ImportError: %s", import_error.msg)
