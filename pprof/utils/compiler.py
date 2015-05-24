from pprof.settings import config
from plumbum import local
from os import path


def lt_clang(flags_to_hide):
    """Return a clang that hides :flags_to_hide: from reordering of libtool.

    This will generate a wrapper script in :p:'s builddir and return a path
    to it.

    :flags_to_hide: the flags libtool is not allowed to see.
    :returns: path to the new clang.

    """
    from plumbum import local
    from os import path

    print_libtool_sucks_wrapper("clang", flags_to_hide, clang)
    return local["./clang"]


def lt_clang_cxx(flags_to_hide):
    """Return a clang++ that hides :flags_to_hide: from reordering of libtool.

    This will generate a wrapper script in :p:'s builddir and return a path
    to it.

    :flags_to_hide: the flags libtool is not allowed to see.
    :returns: path to the new clang++.

    """
    from plumbum import local
    from os import path
    print_libtool_sucks_wrapper("clang++", flags_to_hide, clang_cxx)

    return local["./clang++"]


def print_libtool_sucks_wrapper(filepath, flags_to_hide, compiler):
    """Print a libtool wrapper that hides :flags_to_hide: from libtool.

    :filepath:
        Where should the new compiler be?
    :flags_to_hide:
        List of flags that should be hidden from libtool
    :compiler:
        The compiler we should actually call
    """
    from plumbum.cmd import chmod

    with open(filepath, 'w') as wrapper:
        wrapper.writelines(
            [
                "#!/bin/sh\n",
                'FLAGS="' + " ".join(flags_to_hide) + '"\n',
                str(compiler()) + " $FLAGS $*\n"
            ]
        )
    chmod("+x", filepath)


def llvm():
    return path.join(config["llvmdir"], "bin")


def llvm_libs():
    return path.join(config["llvmdir"], "lib")


def clang_cxx():
    return local[path.join(llvm(), "clang++")]


def clang():
    return local[path.join(llvm(), "clang")]
