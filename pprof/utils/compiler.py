from pprof.settings import config
from plumbum import local
from os import path


def lt_clang(cflags, ldflags):
    """Return a clang that hides :cflags: and :ldflags: from reordering of
    libtool.

    This will generate a wrapper script in :p:'s builddir and return a path
    to it.

    :flags_to_hide: the flags libtool is not allowed to see.
    :cflags: the cflags libtool is not allowed to see.
    :ldflags: the ldflags libtool is not allowed to see.
    :returns: path to the new clang.

    """
    from plumbum import local
    from os import path

    print_libtool_sucks_wrapper("clang", cflags, ldflags, clang)
    return local["./clang"]


def lt_clang_cxx(cflags, ldflags):
    """Return a clang that hides :cflags: and :ldflags: from reordering of
    libtool.

    This will generate a wrapper script in :p:'s builddir and return a path
    to it.

    :flags_to_hide: the flags libtool is not allowed to see.
    :cflags: the cflags libtool is not allowed to see.
    :ldflags: the ldflags libtool is not allowed to see.
    :returns: path to the new clang.

    """
    from plumbum import local
    from os import path
    print_libtool_sucks_wrapper("clang++", cflags, ldflags, clang_cxx)

    return local["./clang++"]


def print_libtool_sucks_wrapper(filepath, cflags, ldflags, compiler):
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
                'CFLAGS="' + " ".join(cflags) + '"\n',
                'LDFLAGS="' + " ".join(ldflags) + '"\n',
                str(compiler()) + " $CFLAGS \"$@\" $LDFLAGS\n"
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
