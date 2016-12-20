import dill
import os
import sys
from plumbum import local
from benchbuild.settings import CFG
from benchbuild.utils.cmd import mv, chmod, rm
from benchbuild.utils.path import list_to_path, template_str
from benchbuild.utils.run import run, uchroot_no_llvm as uchroot

PROJECT_BIN_F_EXT = ".bin"
PROJECT_BLOB_F_EXT = ".postproc"


def strip_path_prefix(ipath, prefix):
    """
    Strip prefix from path.

    Args:
        ipath: input path
        prefix: the prefix to remove, if it is found in :ipath:

    Examples:
        >>> from benchbuild.project import strip_path_prefix
        >>> strip_path_prefix("/foo/bar", "/bar")
        '/foo/bar'
        >>> strip_path_prefix("/foo/bar", "/")
        'foo/bar'
        >>> strip_path_prefix("/foo/bar", "/foo")
        '/bar'
        >>> strip_path_prefix("/foo/bar", "None")
        '/foo/bar'

    """
    if prefix is None:
        return ipath

    return ipath[len(prefix):] if ipath.startswith(prefix) else ipath


def wrap(name, runner, sprefix=None):
    """ Wrap the binary :name: with the function :runner:.

    This module generates a python tool that replaces :name:
    The function in runner only accepts the replaced binaries
    name as argument. We use the cloudpickle package to
    perform the serialization, make sure :runner: can be serialized
    with it and you're fine.

    Args:
        name: Binary we want to wrap
        runner: Function that should run instead of :name:

    Returns:
        A plumbum command, ready to launch.
    """
    name_absolute = os.path.abspath(name)
    real_f = name_absolute + PROJECT_BIN_F_EXT
    if sprefix:
        run(uchroot()["/bin/mv", strip_path_prefix(name_absolute, sprefix),
                      strip_path_prefix(real_f, sprefix)])
    else:
        run(mv[name_absolute, real_f])

    blob_f = name_absolute + PROJECT_BLOB_F_EXT
    with open(blob_f, 'wb') as blob:
        dill.dump(runner, blob, protocol=-1, recurse=True)

    bin_path = list_to_path(CFG["env"]["binary_path"].value())
    bin_path = list_to_path([bin_path, os.environ["PATH"]])

    bin_lib_path = list_to_path(CFG["env"]["binary_ld_library_path"].value())
    bin_lib_path = list_to_path([bin_lib_path, os.environ["LD_LIBRARY_PATH"]])

    with open(name_absolute, 'w') as wrapper:
        lines = template_str("templates/run_static.py.inc")
        lines = lines.format(
            db_host=str(CFG["db"]["host"]),
            db_port=str(CFG["db"]["port"]),
            db_name=str(CFG["db"]["name"]),
            db_user=str(CFG["db"]["user"]),
            db_pass=str(CFG["db"]["pass"]),
            python=sys.executable,
            path=bin_path,
            ld_lib_path=bin_lib_path,
            blobf=strip_path_prefix(blob_f, sprefix),
            runf=strip_path_prefix(real_f, sprefix))
        wrapper.write(lines)
    run(chmod["+x", name_absolute])
    return local[name_absolute]


def wrap_dynamic(self, name, runner, sprefix=None):
    """
    Wrap the binary :name with the function :runner.

    This module generates a python tool :name: that can replace
    a yet unspecified binary.
    It behaves similar to the :wrap: function. However, the first
    argument is the actual binary name.

    Args:
        name: name of the python module
        runner: Function that should run the real binary
        base_class: The base_class of our project.
        base_module: The module of base_class.

    Returns: plumbum command, readty to launch.

    """
    base_class = self.__class__.__name__
    base_module = self.__module__

    name_absolute = os.path.abspath(name)
    blob_f = name_absolute + PROJECT_BLOB_F_EXT
    with open(blob_f, 'wb') as blob:
        blob.write(dill.dumps(runner))

    bin_path = list_to_path(CFG["env"]["binary_path"].value())
    bin_path = list_to_path([bin_path, os.environ["PATH"]])

    bin_lib_path = list_to_path(CFG["env"]["binary_ld_library_path"].value(
    ))
    bin_lib_path = list_to_path([bin_lib_path, os.environ[
        "LD_LIBRARY_PATH"]])

    with open(name_absolute, 'w') as wrapper:
        lines = template_str("templates/run_dynamic.py.inc")
        lines = lines.format(
            db_host=str(CFG["db"]["host"]),
            db_port=str(CFG["db"]["port"]),
            db_name=str(CFG["db"]["name"]),
            db_user=str(CFG["db"]["user"]),
            db_pass=str(CFG["db"]["pass"]),
            python=sys.executable,
            path=bin_path,
            ld_lib_path=bin_lib_path,
            blobf=strip_path_prefix(blob_f, sprefix),
            base_class=base_class,
            base_module=base_module)
        wrapper.write(lines)
    chmod("+x", name_absolute)
    return local[name_absolute]
