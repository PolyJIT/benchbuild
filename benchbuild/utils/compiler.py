"""
Helper functions for dealing with compiler replacement.

This provides a few key functions to deal with varying/measuring the compilers
used inside the benchbuild study.
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
from benchbuild.settings import CFG
from benchbuild.project import PROJECT_BLOB_F_EXT

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
        pi = __get_compiler_paths()
        cc = local[path.join(uchroot_path, cc_name)]
        cc = cc.with_env(LD_LIBRARY_PATH=pi["ld_library_path"])
        return cc
    def gen_compiler_extension(ext): # pylint:  disable=C0111
        return path.join("/", cc_name + ext)
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

    cc_f = abspath(filepath + ".benchbuild.cc")
    with open(cc_f, 'wb') as cc:
        cc.write(dill.dumps(compiler()))
        if compiler_ext_name is not None:
            cc_f = compiler_ext_name(".benchbuild.cc")

    blob_f = abspath(filepath + PROJECT_BLOB_F_EXT)
    if func is not None:
        with open(blob_f, 'wb') as blob:
            blob.write(dill.dumps(func))
        if compiler_ext_name is not None:
            blob_f = compiler_ext_name(PROJECT_BLOB_F_EXT)

    # Update LDFLAGS with configure compiler_ld_library_path. This way
    # the libraries found in LD_LIBRARY_PATH are available at link-time too.
    lib_path_list = CFG["env"]["compiler_ld_library_path"].value()
    ldflags = ldflags + ["-L" + pelem for pelem in lib_path_list if pelem]

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
from benchbuild.utils.run import GuardedRunException
from benchbuild.utils import log

os.environ["BB_CONFIG_FILE"] = "{CFG_FILE}"
from benchbuild.settings import CFG

log.configure()
log = logging.getLogger("benchbuild")
log.addHandler(logging.StreamHandler(stream=sys.stderr))
log.setLevel(logging.DEBUG)

CC_F="{CC_F}"
CC=None
with open(CC_F, "rb") as cc_f:
    CC = dill.load(cc_f)
if not CC:
    log.error("Could not load the compiler command")
    sys.exit(1)

CFLAGS={CFLAGS}
LDFLAGS={LDFLAGS}
BLOB_F="{BLOB_F}"

CFG["db"]["host"] = "{db_host}"
CFG["db"]["port"] = "{db_port}"
CFG["db"]["name"] = "{db_name}"
CFG["db"]["user"] = "{db_user}"
CFG["db"]["pass"] = "{db_pass}"

input_files = [x for x in sys.argv[1:] if not '-' is x[0]]
flags = sys.argv[1:]

def invoke_external_measurement(cmd):
    f = None
    if os.path.exists(BLOB_F):
        with open(BLOB_F,
                  "rb") as p:
            f = dill.load(p)

    if f is not None:
        if not sys.stdin.isatty():
            f(cmd, has_stdin=True)
        else:
            f(cmd)

def run(cmd):
    fc = timeout["2m", cmd]
    fc = fc.with_env(**cmd.envvars)
    retcode, stdout, stderr = (fc & TEE)
    return (retcode, stdout, stderr)

def construct_cc(cc, flags, CFLAGS, LDFLAGS, ifiles):
    fc = None
    if len(input_files) > 0:
        fc = cc["-Qunused-arguments", CFLAGS, LDFLAGS, flags]
    else:
        fc = cc["-Qunused-arguments", flags]
    fc = fc.with_env(**cc.envvars)
    return fc

def construct_cc_default(cc, flags, ifiles):
    fc = None
    fc = cc["-Qunused-arguments", flags]
    fc = fc.with_env(**cc.envvars)
    return fc

def main():
    if 'conftest.c' in input_files:
        retcode, _, _ = (CC[flags] & TEE)
        return retcode
    else:
        fc = construct_cc(CC, flags, CFLAGS, LDFLAGS, input_files)
        try:
            retcode, stdout, stderr = run(fc)
            invoke_external_measurement(fc)
            return retcode
        except ProcessExecutionError:
            fc = construct_cc_default(CC, flags, input_files)
            retcode, stdout, stderr = run(fc)
            return retcode

if __name__ == "__main__":
    retcode = main()
    sys.exit(retcode)
""".format(CC_F=cc_f,
           CFLAGS=cflags,
           LDFLAGS=ldflags,
           BLOB_F=blob_f,
           db_host=str(CFG["db"]["host"]),
           db_name=str(CFG["db"]["name"]),
           db_port=str(CFG["db"]["port"]),
           db_pass=str(CFG["db"]["pass"]),
           db_user=str(CFG["db"]["user"]),
           CFG_FILE=CFG["config_file"].value())
        wrapper.write(lines)
        chmod("+x", filepath)


def llvm():
    """
    Get the path where all llvm binaries can be found.

    Environment variable:
        BB_LLVM_DIR

    Returns:
        LLVM binary path.
    """

    from os import path
    return path.join(str(CFG["llvm"]["dir"]), "bin")


def llvm_libs():
    """
    Get the path where all llvm libraries can be found.

    Environment variable:
        BB_LLVM_DIR

    Returns:
        LLVM library path.
    """
    from os import path
    return path.join(str(CFG["llvm"]["dir"]), "lib")


def __get_compiler_paths():
    from os import getenv
    from benchbuild.utils.path import list_to_path

    path = getenv("PATH", "")
    lib_path = getenv("LD_LIBRARY_PATH", "")
    _lib_path = CFG["env"]["compiler_ld_library_path"].value()
    _path = CFG["env"]["compiler_path"].value()
    _lib_path = list_to_path(_lib_path)
    _path = list_to_path(_path)

    path = list_to_path([_path, path])
    lib_path = list_to_path([_lib_path, lib_path])

    return {"ld_library_path": lib_path, "path": path}

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
    pinfo = __get_compiler_paths()
    clang = local[path.join(llvm(), "clang++")]
    clang = clang.setenv(PATH=pinfo["path"],
                         LD_LIBRARY_PATH=pinfo["ld_library_path"])
    return clang


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
    pinfo = __get_compiler_paths()
    clang = local[path.join(llvm(), "clang")]
    clang = clang.setenv(PATH=pinfo["path"],
                         LD_LIBRARY_PATH=pinfo["ld_library_path"])
    return clang
