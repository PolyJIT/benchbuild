import sys
from types import ModuleType

__ALIASES__ = {"unionfs": ["unionfs_fuse", "unionfs"]}


class CommandAlias(ModuleType):
    """ Module-hack, adapted from plumbum. """
    __all__ = ()
    __package__ = __name__

    def __getattr__(self, command):
        """ Proxy getter for plumbum commands."""
        from os import getenv
        from plumbum import local
        from benchbuild.settings import CFG
        from benchbuild.utils.path import list_to_path
        from benchbuild.utils.path import path_to_list
        import logging

        log = logging.getLogger("benchbuild")
        check = [command]
        if command in __ALIASES__:
            check = __ALIASES__[command]

        path = path_to_list(getenv("PATH", default=""))
        path = CFG["env"]["binary_path"].value() + path

        libs_path = path_to_list(getenv("LD_LIBRARY_PATH", default=""))
        libs_path = CFG["env"]["binary_ld_library_path"].value() + libs_path

        for alias_command in check:
            try:
                cmd = local[alias_command]
                cmd = cmd.with_env(
                    PATH=list_to_path(path),
                    LD_LIBRARY_PATH=list_to_path(libs_path))
                return cmd
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
