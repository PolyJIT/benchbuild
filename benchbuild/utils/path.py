""" Path utilities for benchbuild. """
import os


def list_to_path(pathlist):
    """Convert a list of path elements to a path string."""
    return os.path.pathsep.join(pathlist)


def path_to_list(pathstr):
    """Conver a path string to a list of path elements."""
    return [elem for elem in pathstr.split(os.path.pathsep) if elem]


def determine_path():
    """Borrowed from wxglade.py"""
    try:
        root = __file__
        if os.path.islink(root):
            root = os.path.realpath(root)
        return os.path.dirname(os.path.abspath(root))
    except:
        print("I'm sorry, but something is wrong.")
        print("There is no __file__ variable. Please contact the author.")
        sys.exit()


def template_str(template):
    """Read a template file from the resources and return it as str."""
    tmpl_file = os.path.join(determine_path(), template)
    with open(tmpl_file, mode='r') as tmpl_strm:
        return "".join(tmpl_strm.readlines())
