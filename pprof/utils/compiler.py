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
from pprof.settings import CFG
from pprof.project import PROJECT_BLOB_F_EXT

def wrap_cc_in_uchroot(cflags, ldflags, func=None,
                  uchroot_path=None, cc_name='clang'):
    """
    Generate a clang wrapper that may be called from within a uchroot.

    This basically does the same as lt_clang/lt_clang_cxx. However, we do not
    create a valid plumbum command. The generated script will only work
    inside a uchroot environment that has is root at the current working
    directory, when calling this function.

    Args:
        cflags: The CFLAGS we want to hide
        ldflags: The LDFLAGS we want to hide
        func (optional): A function that will be pickled alongside the compiler.
            It will be called before the actual compilation took place. This
            way you can intercept the compilation process with arbitrary python
            code.
        uchroot_path: Prefix path of the compiler inside the uchroot.
        cc_name: Name of the generated script.
    """
    from os import path
    from plumbum import local

    def gen_compiler(): # pylint:  disable=C0111
        return path.join(uchroot_path, cc_name)
    def gen_compiler_extension(): # pylint:  disable=C0111
        return path.join("/", cc_name + PROJECT_BLOB_F_EXT)
    print_libtool_sucks_wrapper(cc_name, cflags, ldflags, gen_compiler, func,
                                gen_compiler_extension)

def wrap_cxx_in_uchroot(cflags, ldflags, func=None, uchroot_path=None):
    """Delegate to wrap_cc_in_uchroot)."""
    wrap_cc_in_uchroot(cflags, ldflags, func, uchroot_path, 'clang++')

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


def print_libtool_sucks_wrapper(filepath, cflags, ldflags, compiler, func,
                                compiler_ext_name=None):
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
        func: A function that will be pickled alongside the compiler.
            It will be called before the actual compilation took place. This
            way you can intercept the compilation process with arbitrary python
            code.
        compiler_ext_name: The name that we should give to the generated
            dill blob for :func:

    Returns (plumbum.cmd):
        Command of the new compiler we can call.
    """
    from plumbum.cmd import chmod
    import dill
    from os.path import abspath

    blob_f = abspath(filepath + PROJECT_BLOB_F_EXT)
    if func is not None:
        with open(blob_f, 'wb') as blob:
            blob.write(dill.dumps(func))
        if compiler_ext_name is not None:
            blob_f = compiler_ext_name()

    with open(filepath, 'w') as wrapper:
        lines = """#!/usr/bin/env python3
#
import os
import sys
import logging
import dill
import functools
from plumbum import ProcessExecutionError, local
from plumbum.commands.modifiers import TEE
from plumbum.cmd import timeout
from pprof import settings
from pprof.utils.run import GuardedRunException

CC=local["{CC}"]
CFLAGS={CFLAGS}
LDFLAGS={LDFLAGS}
BLOB_F="{BLOB_F}"

DB_HOST="{db_host}"
DB_PORT="{db_port}"
DB_NAME="{db_name}"
DB_USER="{db_user}"
DB_PASS="{db_pass}"

log = logging.getLogger("cc")
log.addHandler(logging.StreamHandler(stream=sys.stderr))

input_files = [x for x in sys.argv[1:] if not '-' is x[0]]
flags = sys.argv[1:]
RETCODE = 0
continuation = None

def run(cmd):
    pass

def invoke_external_measurement(cmd):
    f = None
    with local.env(PPROF_DB_HOST=DB_HOST,
               PPROF_DB_PORT=DB_PORT,
               PPROF_DB_NAME=DB_NAME,
               PPROF_DB_USER=DB_USER,
               PPROF_DB_PASS=DB_PASS):
        if "conftest.c" not in input_files:
            with local.env(PPROF_CMD=str(cmd)):
                if os.path.exists(BLOB_F):
                    with open(BLOB_F,
                              "rb") as p:
                        f = dill.load(p)

                if f is not None:
                    if not sys.stdin.isatty():
                        f(cmd, has_stdin=True)
                    else:
                        f(cmd)

def continue_on_success(retcode, stdout, stderr, cmd):
    invoke_external_measurement(cmd)
    RETCODE=retcode

def continue_on_fail(exc, cmd):
    log.error("Failed to execute - %s", str(cmd))
    log.error(str(exc))
    final_command = CC[flags, LDFLAGS]
    log.warning("New Command: %s", str(final_command))
    _, success = run(final_command)

def run(cmd):
    try:
        log.info("Trying - %s", str(cmd))
        retcode, stdout, stderr = (timeout["2m", cmd.formulate()] & TEE)
        return functools.partial(continue_on_success, retcode, stdout, stderr, cmd), True
    except ProcessExecutionError as exc:
        RETCODE=exc.retcode
        return functools.partial(continue_on_fail, exc, cmd), False

def construct_cc(cc, flags, CFLAGS, LDFLAGS, ifiles):
    if len(input_files) > 0:
        if "-c" in flags:
            final_command = CC["-Qunused-arguments", CFLAGS, LDFLAGS,
                               flags]
        else:
            final_command = CC["-Qunused-arguments", CFLAGS, LDFLAGS,
                               flags]
    else:
        final_command = CC["-Qunused-arguments", flags]
    return final_command

final_command = construct_cc(CC, flags, CFLAGS, LDFLAGS, input_files)
continuation, _ = run(final_command)
continuation()

sys.exit(RETCODE)
""".format(CC=str(compiler()),
           CFLAGS=cflags,
           LDFLAGS=ldflags,
           BLOB_F=blob_f,
           db_host=str(CFG["db"]["host"]),
           db_name=str(CFG["db"]["name"]),
           db_port=str(CFG["db"]["port"]),
           db_pass=str(CFG["db"]["pass"]),
           db_user=str(CFG["db"]["user"]))
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
    return path.join(str(CFG["llvm"]["dir"]), "bin")


def llvm_libs():
    """
    Get the path where all llvm libraries can be found.

    Environment variable:
        PPROF_LLVM_DIR

    Returns:
        LLVM library path.
    """
    from os import path
    return path.join(str(CFG["llvm"]["dir"]), "lib")


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
