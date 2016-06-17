""" Path utilities for benchbuild. """
import os

def list_to_path(pathlist):
    """Convert a list of path elements to a path string."""
    return os.path.pathsep.join(pathlist)

def path_to_list(pathstr):
    """Conver a path string to a list of path elements."""
    return [elem for elem in pathstr.split(os.path.pathsep) if elem]
