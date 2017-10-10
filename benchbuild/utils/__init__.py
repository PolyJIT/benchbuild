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
    def run(self, cmd, _):
        """Simply raises the AttributeError for a missing command."""
        LOG.error("Unable to import %s.", cmd)
        raise AttributeError(cmd)

ERROR = ErrorCommand(__name__ + ".cmd", __name__ + ".cmd")

class CommandAlias(ModuleType):
    """Module-hack, adapted from plumbum."""

    __all__ = ()
    __package__ = __name__
    __overrides__ = {}
    __override_all__ = None

    def __getattr__(self, cmd):
        """Proxy getter for plumbum commands."""
        from os import getenv
        from plumbum import local
        from benchbuild.settings import CFG
        from benchbuild.utils.path import list_to_path
        from benchbuild.utils.path import path_to_list

        check = [cmd]

        if cmd in self.__overrides__:
            check = self.__overrides__[cmd]

        if cmd  in __ALIASES__:
            check = __ALIASES__[cmd]

        path = path_to_list(getenv("PATH", default=""))
        path = CFG["env"]["path"].value() + path

        libs_path = path_to_list(getenv("LD_LIBRARY_PATH", default=""))
        libs_path = CFG["env"]["ld_library_path"].value() + libs_path

        if self.__override_all__ is not None:
            check = [self.__override_all__]

        for alias_command in check:
            try:
                command = local[alias_command]
                command = command.with_env(
                    PATH=list_to_path(path),
                    LD_LIBRARY_PATH=list_to_path(libs_path))
                return cmd
            except AttributeError:
                pass
        LOG.warn("No command found a module. This run will fail.")
        return ERROR

    def __getitem__(self, cmd):
        return self.__getattr__(cmd)

    __path__ = []
    __file__ = __file__


COMMAND = CommandAlias(__name__ + ".cmd", CommandAlias.__doc__)
if not isinstance(COMMAND, ErrorCommand):
    sys.modules[COMMAND.__name__] = COMMAND

del sys
del logging
del ModuleType
del CommandAlias
del BoundCommand
del ErrorCommand
