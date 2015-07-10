from pprof.settings import config


def lt_clang(cflags, ldflags, func=None):
    """Return a clang that hides :cflags: and :ldflags: from reordering of
    libtool.

    This will generate a wrapper script in :p:'s builddir and return a path
    to it.

    :cflags: the cflags libtool is not allowed to see.
    :ldflags: the ldflags libtool is not allowed to see.
    :returns: path to the new clang.

    """
    from plumbum import local

    print_libtool_sucks_wrapper("clang", cflags, ldflags, clang, func)
    return local["./clang"]


def lt_clang_cxx(cflags, ldflags, func=None):
    """Return a clang that hides :cflags: and :ldflags: from reordering of
    libtool.

    This will generate a wrapper script in :p:'s builddir and return a path
    to it.

    :cflags: the cflags libtool is not allowed to see.
    :ldflags: the ldflags libtool is not allowed to see.
    :returns: path to the new clang.

    """
    from plumbum import local

    print_libtool_sucks_wrapper("clang++", cflags, ldflags, clang_cxx, func)
    return local["./clang++"]


def print_libtool_sucks_wrapper(filepath, cflags, ldflags, compiler, func):
    """Print a libtool wrapper that hides :flags_to_hide: from libtool.

    :filepath:
        Where should the new compiler be?
    :flags_to_hide:
        List of flags that should be hidden from libtool
    :compiler:
        The compiler we should actually call
    """
    from plumbum.cmd import chmod
    from cloud.serialization import cloudpickle as cp
    from pprof.project import PROJECT_BLOB_F_EXT
    from os.path import abspath

    blob_f = abspath(filepath + PROJECT_BLOB_F_EXT)
    if func is not None:
        with open(blob_f, 'wb') as b:
            b.write(cp.dumps(func))

    with open(filepath, 'w') as wrapper:
        lines = '''#!/usr/bin/env python
# encoding: utf-8

from plumbum import ProcessExecutionError, local, FG
from pprof.experiment import to_utf8
from os import path
import pickle

from pprof.settings import config
config["db_host"] = "{db_host}"
config["db_port"] = "{db_port}"
config["db_name"] = "{db_name}"
config["db_user"] = "{db_user}"
config["db_pass"] = "{db_pass}"

cc=local[\"{CC}\"]
cflags={CFLAGS}
ldflags={LDFLAGS}

from sys import argv
import os
import sys

def call_original_compiler(input_files, cc, cflags, ldflags, flags):
    final_command = None
    retcode=0
    try:
        if len(input_files) > 0:
            if "-c" in flags:
                final_command = cc["-Qunused-arguments", cflags, ldflags, flags]
            else:
                final_command = cc["-Qunused-arguments", cflags, ldflags, flags]
        else:
            final_command = cc["-Qunused-arguments", flags]

        retcode, stdout, stderr = final_command.run()
        if len(stdout) > 0:
            print stdout
        if len(stderr) > 0:
            print stderr
    except ProcessExecutionError as e:
        #FIXME: Write the fact that we had to fall back to the default
        #compiler somewhere
        cc(flags)
    return (retcode, final_command)


input_files = [ x for x in argv[1:] if not '-' is x[0] ]
flags = argv[1:]
f = None

with local.env(PPROF_DB_HOST="{db_host}",
           PPROF_DB_PORT="{db_port}",
           PPROF_DB_NAME="{db_name}",
           PPROF_DB_USER="{db_user}",
           PPROF_DB_PASS="{db_pass}"):
    retcode, final_cc = call_original_compiler(input_files, cc, cflags,
                                               ldflags, flags)
    """ FIXME: This is just a quick workaround. """
    if "conftest.c" not in input_files:
        with local.env(PPROF_CMD=str(final_cc)):
            if path.exists("{blobf}"):
                with open("{blobf}", "rb") as p:
                    f = pickle.load(p)

            if f is not None:
                if not sys.stdin.isatty():
                    f(final_cc, has_stdin = True)
                else:
                    f(final_cc)
    sys.exit(retcode)
'''.format(CC=str(compiler()), CFLAGS=cflags, LDFLAGS=ldflags,
           blobf=blob_f, db_host=config["db_host"],
           db_name=config["db_name"], db_user=config["db_user"],
           db_pass=config["db_pass"], db_port=config["db_port"])
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
