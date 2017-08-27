import sys
from types import ModuleType

__ALIASES__ = {"unionfs": ["unionfs_fuse", "unionfs"]}


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
                cmd = local[alias_command]
                cmd = cmd.with_env(
                    PATH=list_to_path(path),
                    LD_LIBRARY_PATH=list_to_path(libs_path))
                return cmd
            except AttributeError:
                pass
        raise AttributeError(command)

    def __getitem__(self, command):
        return self.__getattr__(command)

    __path__ = []
    __file__ = __file__


cmd = CommandAlias(__name__ + ".cmd", CommandAlias.__doc__)
sys.modules[cmd.__name__] = cmd

del sys
del ModuleType
del CommandAlias
