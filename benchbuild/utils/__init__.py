"""
Module handler that makes sure the modules for our commands are build similar
to plumbum. The built modules are only active during a run of an experiment and
get deleted afterwards.
"""
import sys
import logging
from types import ModuleType
from plumbum.commands.base import BoundCommand

__ALIASES__ = {"unionfs": ["unionfs_fuse", "unionfs"]}
LOG = logging.getLogger(__name__)


class ErrorCommand(BoundCommand):
    """
    A command that raises an exception when it gets called.
    This allows us to call the study with experiments who use incorrect imports,
    without the entire study to crash.
    The experiment will fail anyway, but without the entire programm crashing.
    """
    def run(self, *args, **kwargs):
        """Simply raises the AttributeError for a missing command."""
        LOG.error("Unable to import a needed module.")
        raise AttributeError(__name__ + ".cmd")

ERROR = ErrorCommand(__name__ + ".cmd", ErrorCommand.__doc__)

class CommandAlias(ModuleType):
    """Module-hack, adapted from plumbum."""

    __all__ = ()
    __package__ = __name__
    __overrides__ = {}
    __override_all__ = None

    def __getattr__(self, command):
        """Proxy getter for plumbum commands."""
        from os import getenv
        from plumbum import local
        from benchbuild.settings import CFG
        from benchbuild.utils.path import list_to_path
        from benchbuild.utils.path import path_to_list

        check = [command]

        if command in self.__overrides__:
            check = self.__overrides__[command]

        if command in __ALIASES__:
            check = __ALIASES__[command]

        path = path_to_list(getenv("PATH", default=""))
        path = CFG["env"]["path"].value() + path

        libs_path = path_to_list(getenv("LD_LIBRARY_PATH", default=""))
        libs_path = CFG["env"]["ld_library_path"].value() + libs_path

        if self.__override_all__ is not None:
            check = [self.__override_all__]

        for alias_command in check:
            try:
                alias_cmd = local[alias_command]
                alias_cmd = alias_cmd.with_env(
                    PATH=list_to_path(path),
                    LD_LIBRARY_PATH=list_to_path(libs_path))
                return alias_cmd
            except AttributeError:
                pass
        LOG.warning("'%s' cannot be found. Import failed.", command)
        return ERROR

    def __getitem__(self, command):
        return self.__getattr__(command)

    __path__ = []
    __file__ = __file__


cmd = CommandAlias(__name__ + ".cmd", CommandAlias.__doc__)
sys.modules[cmd.__name__] = cmd

del sys
del logging
del ModuleType
del CommandAlias
del BoundCommand
del ErrorCommand
