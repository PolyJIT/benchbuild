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
    * wrap_cc()

The remaining methods:
    * llvm()
    * llvm_libs()
    * clang()
    * clang_cxx()

Are just convencience methods that can be used when interacting with the
configured llvm/clang source directories.
"""
from benchbuild.settings import CFG
from benchbuild.utils.wrapping import wrap_cc
from plumbum.commands.base import BoundCommand


def wrap_cc_in_uchroot(cflags, ldflags, func=None, cc_name='clang'):
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

    def compiler():  # pylint:  disable=C0111
        pi = __get_paths()
        cc = local["/usr/bin/env"]
        cc = cc[cc_name]
        cc = cc.with_env(LD_LIBRARY_PATH=pi["ld_library_path"])
        return cc

    def gen_compiler_extension(ext):  # pylint:  disable=C0111
        return path.join("/", cc_name + ext)
    wrap_cc(cc_name, cflags, ldflags, compiler, func, gen_compiler_extension,
            python="/usr/bin/env python3")


def wrap_cxx_in_uchroot(cflags, ldflags, func=None):
    """Delegate to wrap_cc_in_uchroot)."""
    wrap_cc_in_uchroot(cflags, ldflags, func, 'clang++')


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

    Returns (benchbuild.utils.cmd):
        Path to the new clang command.
    """
    from benchbuild.utils import cmd

    wrap_cc("clang", cflags, ldflags, clang, func)
    return cmd["./clang"]


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

    Returns (benchbuild.utils.cmd):
        Path to the new clang command.
    """
    from plumbum import local

    wrap_cc("clang++", cflags, ldflags, clang_cxx, func)
    return local["./clang++"]


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


def __get_paths():
    from os import getenv
    from benchbuild.utils.path import list_to_path

    path = getenv("PATH", "")
    lib_path = getenv("LD_LIBRARY_PATH", "")
    _lib_path = CFG["env"]["ld_library_path"].value()
    _path = CFG["env"]["path"].value()
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
    pinfo = __get_paths()
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
    pinfo = __get_paths()
    clang = local[path.join(llvm(), "clang")]
    clang = clang.setenv(PATH=pinfo["path"],
                         LD_LIBRARY_PATH=pinfo["ld_library_path"])
    return clang


class ExperimentCommand(BoundCommand):
    __slots__ = ["cmd", "args"]

    def __init__(self, cmd, args, exp_args):
        self.cmd = cmd
        self.args = args if args is not None else []
        for inner_list in list(exp_args):
            self.args.extend(inner_list)
