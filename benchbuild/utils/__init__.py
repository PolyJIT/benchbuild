import sys
from types import ModuleType

__ALIASES__ = {"unionfs": ["unionfs_fuse", "unionfs"]}


class CommandAlias(ModuleType):
    """ Module-hack, adapted from plumbum. """
    __all__ = ()
    __package__ = __name__

    def __getattr__(self, command):
        """ Proxy getter for plumbum commands."""
        from plumbum import local
        check = [command]
        if command in __ALIASES__:
            check = __ALIASES__[command]

        for alias_command in check:
            try:
                return local[alias_command]
            except AttributeError:
                pass
        raise AttributeError(command)

    __path__ = []
    __file__ = __file__


cmd = CommandAlias(__name__ + ".cmd", CommandAlias.__doc__)
sys.modules[cmd.__name__] = cmd

del sys
del ModuleType
del CommandAlias
