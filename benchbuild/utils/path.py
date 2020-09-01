""" Path utilities for benchbuild. """
import fcntl
import os
from contextlib import contextmanager
from typing import List, Optional

import benchbuild.utils.user_interface as ui


def list_to_path(pathlist: List[str]) -> str:
    """
    Convert a list of path elements to a path string.

    Args:
        pathlist: List of path components to be joined

    Returns:
        joined path components as single str.
    """
    return os.path.pathsep.join(pathlist)


def path_to_list(pathstr: str) -> List[str]:
    """
    Convert a path string to a list of path elements.

    Args:
        pathstr: path-like string.

    Returns:
        List of path components as str.
    """
    return [elem for elem in pathstr.split(os.path.pathsep) if elem]


def __self__() -> str:
    """
    Borrowed from wxglade.py

    Returns:
        Absolute path of this module
    """
    root = __file__
    if os.path.islink(root):
        root = os.path.realpath(root)
    return os.path.dirname(os.path.abspath(root))


__ROOT__ = __self__()
__RESOURCES_ROOT__ = os.path.join(__ROOT__, '..', 'res')


def template_files(path: str, exts: Optional[List[str]] = None) -> List[str]:
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
        _path = os.path.join(__RESOURCES_ROOT__, path)
    if not (os.path.exists(_path) and os.path.isdir(_path)):
        return []
    if not exts:
        exts = []
    files = os.listdir(_path)
    files = [f for f in files if os.path.splitext(f)[-1] in exts]
    files = [os.path.join(path, f) for f in files]
    return files


def template_path(template: str) -> str:
    """
    Return path to template file.

    Args:
        template: relative template path
    Returns:
        absolute path to the given template.
    """
    return os.path.join(__RESOURCES_ROOT__, template)


def template_str(template: str) -> str:
    """
    Read a template file from the resources and return it as str.

    Args:
        template: relative template path

    Returns:
        template content as a single string.
    """
    tmpl_file = template_path(template)
    with open(tmpl_file, mode='r') as tmpl_strm:
        return "".join(tmpl_strm.readlines())


def mkdir_interactive(dirpath: str) -> None:
    """
    Create a directory if required.

    This will query the user for a confirmation.

    Args:
        dirname: The path to create.
    """
    from benchbuild.utils.cmd import mkdir

    if os.path.exists(dirpath):
        return

    response = ui.ask("The directory {dirname} does not exist yet. "
                      "Should I create it?".format(dirname=dirpath),
                      default_answer=True,
                      default_answer_str="yes")

    if response:
        mkdir("-p", dirpath)
        print("Created directory {0}.".format(dirpath))


@contextmanager
def flocked(filename: str, lock_type: int = fcntl.LOCK_EX):
    """
    Lock a section using fcntl.

    Args:
        filename: the file to lock against.
                  A file descriptor is opened in
                  append mode to this path.
        lock_type: one of fcntl's lock operations

    Yields:
        the opened file descriptor we hold the lock for.
    """
    with open(filename, 'a') as fd:
        try:
            fcntl.flock(fd, lock_type)
            yield fd
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
