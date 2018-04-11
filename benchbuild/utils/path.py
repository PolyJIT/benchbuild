""" Path utilities for benchbuild. """
import os
import sys

import benchbuild.utils.user_interface as ui


def list_to_path(pathlist):
    """Convert a list of path elements to a path string."""
    return os.path.pathsep.join(pathlist)


def path_to_list(pathstr):
    """Conver a path string to a list of path elements."""
    return [elem for elem in pathstr.split(os.path.pathsep) if elem]


def determine_path():
    """Borrowed from wxglade.py"""
    root = __file__
    if os.path.islink(root):
        root = os.path.realpath(root)
    return os.path.dirname(os.path.abspath(root))

def template_files(path, exts=None):
    """
    Return a list of filenames found at @path.

    The list of filenames can be filtered by extensions.

    Arguments:
        path: Existing filepath we want to list.
        exts: List of extensions to filter by.

    Returns:
        A list of filenames found in the path.
    """
    if not os.path.isabs(path):
        _path = os.path.join(determine_path(), path)
    if not (os.path.exists(_path) and os.path.isdir(_path)):
        return []
    if not exts:
        exts = []
    files = os.listdir(_path)
    files = [f for f in files if os.path.splitext(f)[-1] in exts]
    files = [os.path.join(path, f) for f in files]
    return files

def template_path(template):
    """Return path to template file."""
    return os.path.join(determine_path(), template)

def template_str(template):
    """Read a template file from the resources and return it as str."""
    tmpl_file = os.path.join(determine_path(), template)
    with open(tmpl_file, mode='r') as tmpl_strm:
        return "".join(tmpl_strm.readlines())


def mkfile_uchroot(filepath, root="."):
    """
    Create a file inside a uchroot env.

    You will want to use this when you need to create a file with apropriate
    rights inside a uchroot container with subuid/subgid handling enabled.

    Args:
        filepath:
            The filepath that should be created. Absolute inside the
            uchroot container.
        root:
            The root PATH of the container filesystem as seen outside of
            the container.
    """
    from benchbuild.utils.run import uchroot_no_args, uretry


    uchroot = uchroot_no_args()
    uchroot = uchroot["-E", "-A", "-C", "-w", "/", "-r"]
    uchroot = uchroot[os.path.abspath(root)]
    uretry(uchroot["--", "/bin/touch", filepath])


def mkdir_uchroot(dirpath, root="."):
    """
    Create a file inside a uchroot env.

    You will want to use this when you need to create a file with apropriate
    rights inside a uchroot container with subuid/subgid handling enabled.

    Args:
        dirpath:
            The dirpath that should be created. Absolute inside the
            uchroot container.
        root:
            The root PATH of the container filesystem as seen outside of
            the container.
    """
    from benchbuild.utils.run import uchroot_no_args, uretry

    uchroot = uchroot_no_args()
    uchroot = uchroot["-E", "-A", "-C", "-w", "/", "-r"]
    uchroot = uchroot[os.path.abspath(root)]
    uretry(uchroot["--", "/bin/mkdir", "-p", dirpath])


def mkdir_interactive(dirpath):
    """
    Create a directory if required.

    This will query the user for a confirmation.

    Args:
        dirname: The path to create.
    """
    from benchbuild.utils.cmd import mkdir
    if os.path.exists(dirpath):
        return

    response = True
    if sys.stdin.isatty():
        response = ui.query_yes_no(
            "The build directory {dirname} does not exist yet. "
            "Should I create it?".format(dirname=dirpath),
            "no")

    if response:
        mkdir("-p", dirpath)
        print("Created directory {0}.".format(dirpath))
