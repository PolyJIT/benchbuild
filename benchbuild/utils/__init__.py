"""
Module handler that makes sure the modules for our commands are build similar
to plumbum. The built modules are only active during a run of an experiment and
get deleted afterwards.
"""
import logging
import os
import sys
import typing as tp
from types import ModuleType

import plumbum as pb
from plumbum.machines.local import LocalCommand

__ALIASES__ = {"unionfs": ["unionfs_fuse", "unionfs"]}
LOG = logging.getLogger(__name__)


class ErrorCommand(LocalCommand):
    """
    A command that raises an exception when it gets called.
    This allows us to call the study with experiments who use incorrect imports,
    without the entire study to crash.
    The experiment will fail anyway, but without the entire programm crashing.
    """
    EXE = __name__ + ".error_cmd"

    def run(self, *args, **kwargs):
        """Simply raises the AttributeError for a missing command."""
        LOG.error("Unable to import a needed module.")
        raise AttributeError(self.EXE)

    def popen(self, *args, **kwargs):
        """Simply raises the AttributeError for a missing command."""
        LOG.error("Unable to import a needed module.")
        raise AttributeError(self.EXE)

    def __len__(self) -> int:
        return len(self.EXE)


ERROR = ErrorCommand(__name__ + ".cmd")


class CommandAlias(ModuleType):
    """Module-hack, adapted from plumbum."""

    __all__ = ()
    __package__ = __name__
    __overrides__ = {}
    __override_all__ = None

    def __getattr__(self, command: str) -> pb.commands.ConcreteCommand:
        """Proxy getter for plumbum commands."""
        from benchbuild.settings import CFG
        from benchbuild.utils.path import list_to_path
        from benchbuild.utils.path import path_to_list

        check = [command]

        if command in self.__overrides__:
            check = self.__overrides__[command]

        check.extend(__ALIASES__.get(command, [command]))

        env = CFG["env"].value
        path = path_to_list(os.getenv("PATH", ""))
        path.extend(env.get("PATH", []))

        libs_path = path_to_list(os.getenv("LD_LIBRARY_PATH", ""))
        libs_path.extend(env.get("LD_LIBRARY_PATH", []))

        home = env.get("HOME", os.getenv("HOME", ""))

        if self.__override_all__ is not None:
            check = [self.__override_all__]

        for alias_command in check:
            try:
                alias_cmd = pb.local[alias_command]
                alias_cmd = alias_cmd.with_env(
                    PATH=list_to_path(path),
                    LD_LIBRARY_PATH=list_to_path(libs_path),
                    HOME=home
                )
                return alias_cmd
            except AttributeError:
                pass
        LOG.debug("'%s' cannot be found. Import failed.", command)
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
del LocalCommand
