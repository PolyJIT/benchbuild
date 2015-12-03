"""
Helper functions for dealing with compiler replacement.

This provides a few key functions to deal with varying/measuring the compilers
used inside the pprof study.
From a high-level view, there are 2 interesting functions:
    * lt_clang(cflags, ldflags, func)
    * lt_clang_cxx(cflags, ldflags, func)

These generate a wrapped clang/clang++ in the current working directory and
hide the given cflags/ldflags from the calling build system. Both will
give you a working plumbum command and call a python script that redirects
to the real clang/clang++ given the additional cflags&ldflags.

The wrapper-script generated for both functions can be found inside:
    * print_libtool_sucks_wrapper()

The remaining methods:
    * llvm()
    * llvm_libs()
    * clang()
    * clang_cxx()

Are just convencience methods that can be used when interacting with the
configured llvm/clang source directories.
"""
from pprof.settings import config


def lt_clang(cflags, ldflags, func=None):
    """
    Return a clang that hides CFLAGS and LDFLAGS.

    This will generate a wrapper script in the current directory
    and return a complete plumbum command to it.

    Args:
        cflags: The CFLAGS we want to hide.
        ldflags: The LDFLAGS we want to hide.
        func (optional): A function that will be pickled alongside the compiler.
            It will be called before the actual compilation took place. This
            way you can intercept the compilation process with arbitrary python
            code.

    Returns (plumbum.cmd):
        Path to the new clang command.
    """
    from plumbum import local

    print_libtool_sucks_wrapper("clang", cflags, ldflags, clang, func)
    return local["./clang"]


def lt_clang_cxx(cflags, ldflags, func=None):
    """
    Return a clang++ that hides CFLAGS and LDFLAGS.

    This will generate a wrapper script in the current directory
    and return a complete plumbum command to it.

    Args:
        cflags: The CFLAGS we want to hide.
        ldflags: The LDFLAGS we want to hide.
        func (optional): A function that will be pickled alongside the compiler.
            It will be called before the actual compilation took place. This
            way you can intercept the compilation process with arbitrary python
            code.

    Returns (plumbum.cmd):
        Path to the new clang command.
    """
    from plumbum import local

    print_libtool_sucks_wrapper("clang++", cflags, ldflags, clang_cxx, func)
    return local["./clang++"]


def print_libtool_sucks_wrapper(filepath, cflags, ldflags, compiler, func):
    """
    Substitute a compiler with a script that hides CFLAGS & LDFLAGS.

    This will generate a wrapper script in the current directory
    and return a complete plumbum command to it.

    Args:
        filepath (str): Path to the wrapper script.
        cflags (list(str)): The CFLAGS we want to hide.
        ldflags (list(str)): The LDFLAGS we want to hide.
        compiler (plumbum.cmd): Real compiler command we should call in the
            script.

    Returns (plumbum.cmd):
        Command of the new compiler we can call.
    """
    from plumbum.cmd import chmod
    from cloud.serialization import cloudpickle as cp
    from pprof.project import PROJECT_BLOB_F_EXT
    from os.path import abspath

    blob_f = abspath(filepath + PROJECT_BLOB_F_EXT)
    if func is not None:
        with open(blob_f, 'wb') as blob:
            blob.write(cp.dumps(func))

    with open(filepath, 'w') as wrapper:
        lines = '''#!/usr/bin/env python
# 

from plumbum import ProcessExecutionError, local, FG
from plumbum.commands.modifiers import TEE
from pprof.utils.run import GuardedRunException
from pprof.experiment import to_utf8
from os import path
import logging
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

log = logging.getLogger("clang")
log.addHandler(logging.StreamHandler(stream=sys.stderr))

def really_exec(cmd):
    from plumbum.cmd import timeout
    try:
        log.info("Trying - %s", str(cmd))
        return ( timeout["2m", cmd.formulate()] & TEE )
    except (GuardedRunException, ProcessExecutionError) as e:
        log.error("Failed to execute - %s", str(cmd))
        raise e


def call_original_compiler(input_files, cc, cflags, ldflags, flags):
    final_command = None
    retcode=0
    try:
        if len(input_files) > 0:
            if "-c" in flags:
                final_command = cc["-Qunused-arguments", cflags, ldflags, flags]
            else:
                final_command = cc["-Qunused-arguments", cflags, flags, ldflags]
        else:
            final_command = cc["-Qunused-arguments", flags]

        retcode, stdout, stderr = really_exec(final_command)

    except (GuardedRunException, ProcessExecutionError) as e:
        log.warn("Fallback to original flags and retry.")
        final_command = cc[flags, ldflags]
        log.warn("New Command: %s", str(final_command))
        retcode, _, _ = really_exec(final_command)

    return (retcode, final_command)


input_files = [ x for x in argv[1:] if not '-' is x[0] ]
flags = argv[1:]
f = None

retcode, final_cc = call_original_compiler(input_files, cc, cflags, ldflags,
                                           flags)

with local.env(PPROF_DB_HOST="{db_host}",
           PPROF_DB_PORT="{db_port}",
           PPROF_DB_NAME="{db_name}",
           PPROF_DB_USER="{db_user}",
           PPROF_DB_PASS="{db_pass}"):
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
'''.format(CC=str(compiler()),
           CFLAGS=cflags,
           LDFLAGS=ldflags,
           blobf=blob_f,
           db_host=config["db_host"],
           db_name=config["db_name"],
           db_user=config["db_user"],
           db_pass=config["db_pass"],
           db_port=config["db_port"])
        wrapper.write(lines)
        chmod("+x", filepath)


def llvm():
    """
    Get the path where all llvm binaries can be found.

    Environment variable:
        PPROF_LLVM_DIR

    Returns:
        LLVM binary path.
    """

    from os import path
    return path.join(config["llvmdir"], "bin")


def llvm_libs():
    """
    Get the path where all llvm libraries can be found.

    Environment variable:
        PPROF_LLVM_DIR

    Returns:
        LLVM library path.
    """
    from os import path
    return path.join(config["llvmdir"], "lib")


def clang_cxx():
    """
    Get a usable clang++ plumbum command.

    This searches for a usable clang++ in the llvm binary path (See llvm()) and
    returns a plumbum command to call it.

    Returns:
        plumbum Command that executes clang++
    """
    from os import path
    from plumbum import local
    return local[path.join(llvm(), "clang++")]


def clang():
    """
    Get a usable clang plumbum command.

    This searches for a usable clang in the llvm binary path (See llvm()) and
    returns a plumbum command to call it.

    Returns:
        plumbum Command that executes clang++
    """
    from os import path
    from plumbum import local
    return local[path.join(llvm(), "clang")]
