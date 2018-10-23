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

from benchbuild.settings import CFG
from benchbuild.utils.wrapping import wrap_cc


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

    cxx_name = str(CFG["compiler"]["cxx"])
    wrap_cc(
        cxx_name, compiler(cxx_name), project, detect_project=detect_project)
    return cmd["./{name}".format(name=cxx_name)]


def __get_paths():
    from os import getenv
    from benchbuild.utils.path import list_to_path

    path = getenv("PATH", "")
    lib_path = getenv("LD_LIBRARY_PATH", "")
    env = CFG["env"].value

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
    return _compiler
