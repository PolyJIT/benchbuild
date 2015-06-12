from pprof.settings import config


def lt_clang(cflags, ldflags):
    """Return a clang that hides :cflags: and :ldflags: from reordering of
    libtool.

    This will generate a wrapper script in :p:'s builddir and return a path
    to it.

    :cflags: the cflags libtool is not allowed to see.
    :ldflags: the ldflags libtool is not allowed to see.
    :returns: path to the new clang.

    """
    from plumbum import local

    print_libtool_sucks_wrapper("clang", cflags, ldflags, clang)
    return local["./clang"]


def lt_clang_cxx(cflags, ldflags):
    """Return a clang that hides :cflags: and :ldflags: from reordering of
    libtool.

    This will generate a wrapper script in :p:'s builddir and return a path
    to it.

    :cflags: the cflags libtool is not allowed to see.
    :ldflags: the ldflags libtool is not allowed to see.
    :returns: path to the new clang.

    """
    from plumbum import local
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
        lines = '''#!/usr/bin/env python
# encoding: utf-8

from plumbum import ProcessExecutionError, local, FG
from pprof.experiment import to_utf8

cc=local[\"{CC}\"]
cflags={CFLAGS}
ldflags={LDFLAGS}

from sys import argv
import os
import sys

input_files = [ x for x in argv[1:] if not '-' is x[0] ]
flags = argv[1:]

try:
    if len(input_files) > 0:
        if "-c" in argv:
            cc["-Qunused-arguments", cflags, flags] & FG
        else:
            cc["-Qunused-arguments", cflags, flags, ldflags] & FG
    else:
        cc["-Qunused-arguments", flags] & FG
except ProcessExecutionError as e:
    sys.stderr.write(to_utf8(str(e.stderr)))
    sys.stderr.flush()
    sys.exit(e.retcode)


'''.format(CC=str(compiler()), CFLAGS=cflags, LDFLAGS=ldflags)
        wrapper.write(lines)
    chmod("+x", filepath)


def llvm():
    from os import path
    return path.join(config["llvmdir"], "bin")


def llvm_libs():
    from os import path
    return path.join(config["llvmdir"], "lib")


def clang_cxx():
    from os import path
    from plumbum import local
    return local[path.join(llvm(), "clang++")]


def clang():
    from os import path
    from plumbum import local
    return local[path.join(llvm(), "clang")]
