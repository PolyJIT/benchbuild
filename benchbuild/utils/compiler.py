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
from plumbum.commands.base import BoundCommand

from benchbuild.settings import CFG
from benchbuild.utils.wrapping import wrap_cc


def wrap_cc_in_uchroot(project, cc_name='cc'):
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
    from os import path

    def gen_compiler_extension(ext):
        return path.join("/", cc_name + ext)
    wrap_cc(cc_name, compiler, project, gen_compiler_extension,
            python="/usr/bin/env python3")


def wrap_cxx_in_uchroot(project):
    """Delegate to wrap_cc_in_uchroot)."""
    wrap_cc_in_uchroot(project, CFG["compiler"]["cxx"].value())


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

    cc = CFG["compiler"]["c"].value()
    wrap_cc(cc, compiler(cc), project, detect_project=detect_project)
    return cmd["./{name}".format(name=cc)]


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
    _lib_path = CFG["env"]["ld_library_path"].value()
    _path = CFG["env"]["path"].value()
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
    from plumbum import local
    pinfo = __get_paths()
    _compiler = local[name]
    _compiler = _compiler.setenv(PATH=pinfo["path"],
                                 LD_LIBRARY_PATH=pinfo["ld_library_path"])
    return lambda : _compiler


class ExperimentCommand(BoundCommand):
    __slots__ = ["cmd", "args"]

    def __init__(self, cmd, args, exp_args):
        self.cmd = cmd
        self.args = args if args is not None else []
        for inner_list in list(exp_args):
            self.args.extend(inner_list)
