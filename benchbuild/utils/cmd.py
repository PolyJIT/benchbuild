import sys

__ALIASES__ = {"unionfs": ["unionfs_fuse", "unionfs"]}


class CommandAlias:
    def __getattr__(self, command):
        """ Proxy getter for plumbum commands."""
        from plumbum import cmd
        check = [command]
        if command in __ALIASES__:
            check = __ALIASES__[command]

        for alias_command in check:
            try:
                symbol = cmd.__getattr__(alias_command)
                return symbol
            except AttributeError:
                pass
        raise AttributeError


sys.modules[__name__] = CommandAlias()
