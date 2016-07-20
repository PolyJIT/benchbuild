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
    from benchbuild.utils.run import uchroot_no_args

    uchroot = uchroot_no_args()
    uchroot = uchroot["-E", "-A", "-C", "-r", "/", "-w"]
    uchroot = uchroot[os.path.abspath(root)]
    uchroot("--", "/bin/touch", filepath)


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
    from benchbuild.utils.run import uchroot_no_args

    uchroot = uchroot_no_args()
    uchroot = uchroot["-E", "-A", "-C", "-r", "/", "-w"]
    uchroot = uchroot[os.path.abspath(root)]
    uchroot("--", "/bin/mkdir", "-p", dirpath)
