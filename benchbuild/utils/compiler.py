"""
Helper functions for dealing with compiler replacement.

This provides a few key functions to deal with varying/measuring the compilers
used inside the benchbuild study.
From a high-level view, there are 2 interesting functions:
    * cc(project, detect_project=True)
    * cxx(project, detect_project=True)

These generate a wrapped clang/clang++ in the current working directory and
hide the given cflags/ldflags from the calling build system. Both will
give you a working plumbum command and call a python script that redirects
to the real clang/clang++ given the additional cflags&ldflags.

The wrapper-script generated for both functions can be found inside:
    * wrap_cc()

Are just convencience methods that can be used when interacting with the
configured llvm/clang source directories.
"""
from plumbum import local
from plumbum.commands.base import BoundCommand

from benchbuild.settings import CFG
from benchbuild.utils.wrapping import wrap_cc


def wrap_cc_in_uchroot(project, cc_name=None):
    """
    Generate a clang wrapper that may be called from within a uchroot.

    This basically does the same as cc/cxx. However, we do not
    create a valid plumbum command. The generated script will only work
    inside a uchroot environment that has is root at the current working
    directory, when calling this function.

    Args:
        project: The project we generate this compiler for.
        cc_name: Name of the generated script.
    """
    if not cc_name:
        cc_name = str(CFG["compiler"]["c"])

    wrap_cc(
        cc_name,
        compiler(cc_name),
        project,
        lambda ext: local.path("/") / ext,
        python="/usr/bin/env python3")


def wrap_cxx_in_uchroot(project):
    """Delegate to wrap_cc_in_uchroot)."""
    wrap_cc_in_uchroot(project, str(CFG["compiler"]["cxx"]))


def cc(project, detect_project=False):
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

    cc_name = str(CFG["compiler"]["c"])
    wrap_cc(cc_name, compiler(cc_name), project, detect_project=detect_project)
    return cmd["./{}".format(cc_name)]


def cxx(project, detect_project=False):
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
    from benchbuild.utils import cmd

    cxx = CFG["compiler"]["cxx"].value()
    wrap_cc(cxx, compiler(cxx), project, detect_project=detect_project)
    return cmd["./{name}".format(name=cxx)]


def __get_paths():
    from os import getenv
    from benchbuild.utils.path import list_to_path

    path = getenv("PATH", "")
    lib_path = getenv("LD_LIBRARY_PATH", "")
    env = CFG["env"].value()

    _lib_path = env.get("LD_LIBRARY_PATH", "")
    _path = env.get("PATH", "")

    _lib_path = list_to_path(_lib_path)
    _path = list_to_path(_path)

    path = list_to_path([_path, path])
    lib_path = list_to_path([_lib_path, lib_path])

    return {"ld_library_path": lib_path, "path": path}


def compiler(name):
    """
    Get a usable clang++ plumbum command.

    This searches for a usable clang++ in the llvm binary path

    Returns:
        plumbum Command that executes clang++
    """
    pinfo = __get_paths()
    _compiler = local[name]
    _compiler = _compiler.setenv(
        PATH=pinfo["path"], LD_LIBRARY_PATH=pinfo["ld_library_path"])
    return lambda: _compiler
