"""
Wrapper utilities for benchbuild.

This module provides methods to wrap binaries with extensions that are
pickled alongside the original binary.
In place of the original binary a new python module is generated that
loads the pickle and redirects the program call with all its arguments
to it. This allows interception of arbitrary programs for experimentation.

Examples:
    TODO

Compiler Wrappers:
    The compiler wrappers substitute the compiler call with a script that
    produces the expected output from the original compiler call first.
    Afterwards the pickle is loaded and the original call is forwarded to the
    pickle. This way the user is not obligated to produce valid output during
    his own experiment.

Runtime Wrappers:
    These directly forward the binary call to the pickle without any execution
    of the binary. We cannot guarantee that repeated execution is valid,
    therefore, we let the user decide what the program should do.
"""
import logging
import os
import sys
import typing as tp
from typing import TYPE_CHECKING

import dill
import jinja2
import plumbum as pb
from plumbum import local
from plumbum.commands.base import BoundCommand

from benchbuild.settings import CFG
from benchbuild.utils import run
from benchbuild.utils.cmd import chmod, mv
from benchbuild.utils.path import list_to_path
from benchbuild.utils.uchroot import no_llvm as uchroot

PROJECT_BIN_F_EXT = ".bin"
PROJECT_BLOB_F_EXT = ".postproc"
LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    from benchbuild.project import Project
    from benchbuild.experiment import Experiment


def strip_path_prefix(ipath: str, prefix: str) -> str:
    """
    Strip prefix from path.

    Args:
        ipath: input path
        prefix: the prefix to remove, if it is found in :ipath:

    Examples:
        >>> strip_path_prefix("/foo/bar", "/bar")
        '/foo/bar'
        >>> strip_path_prefix("/foo/bar", "/")
        'foo/bar'
        >>> strip_path_prefix("/foo/bar", "/foo")
        '/bar'
        >>> strip_path_prefix("/foo/bar", "None")
        '/foo/bar'

    """
    if not prefix:
        return ipath

    return ipath[len(prefix):] if ipath.startswith(prefix) else ipath


def unpickle(pickle_file: str) -> tp.Any:
    """Unpickle a python object from the given path."""
    pickle = None
    with open(pickle_file, "rb") as pickle_f:
        pickle = dill.load(pickle_f)
    if not pickle:
        LOG.error("Could not load python object from file")
    return pickle


def __create_jinja_env() -> jinja2.Environment:
    return jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        loader=jinja2.PackageLoader('benchbuild', 'res')
    )


def wrap(
    name: str,
    project: 'Project',
    sprefix: str = '',
    python: str = sys.executable
) -> pb.commands.ConcreteCommand:
    """ Wrap the binary :name: with the runtime extension of the project.

    This module generates a python tool that replaces :name:
    The function in runner only accepts the replaced binaries
    name as argument. We use the cloudpickle package to
    perform the serialization, make sure :runner: can be serialized
    with it and you're fine.

    Args:
        name: Binary we want to wrap
        project: The project that contains the runtime_extension we want
                 to run instead of the binary.

    Returns:
        A plumbum command, ready to launch.
    """
    env = __create_jinja_env()
    template = env.get_template('wrapping/run_static.py.inc')

    name_absolute = os.path.abspath(name)
    real_f = name_absolute + PROJECT_BIN_F_EXT
    if sprefix:
        _mv = run.watch(uchroot()["/bin/mv"])
        _mv(
            strip_path_prefix(name_absolute, sprefix),
            strip_path_prefix(real_f, sprefix)
        )
    else:
        _mv = run.watch(mv)
        _mv(name_absolute, real_f)

    project_file = persist(project, suffix=".project")

    env = CFG['env'].value

    bin_path = list_to_path(env.get('PATH', []))
    bin_path = list_to_path([bin_path, os.environ["PATH"]])

    bin_lib_path = list_to_path(env.get('LD_LIBRARY_PATH', []))
    bin_lib_path = list_to_path([bin_lib_path, os.environ["LD_LIBRARY_PATH"]])
    home = env.get("HOME", os.getenv("HOME", ""))

    with open(name_absolute, 'w') as wrapper:
        wrapper.write(
            template.render(
                runf=strip_path_prefix(real_f, sprefix),
                project_file=strip_path_prefix(project_file, sprefix),
                path=str(bin_path),
                ld_library_path=str(bin_lib_path),
                home=str(home),
                python=python,
            )
        )

    _chmod = run.watch(chmod)
    _chmod("+x", name_absolute)
    return local[name_absolute]


def wrap_dynamic(
    project: 'Project',
    name: str,
    sprefix: str = '',
    python: str = sys.executable,
    name_filters: tp.Optional[tp.List[str]] = None
) -> BoundCommand:
    """
    Wrap the binary :name with the function :runner.

    This module generates a python tool :name: that can replace
    a yet unspecified binary.
    It behaves similar to the :wrap: function. However, the first
    argument is the actual binary name.

    Args:
        name: name of the python module
        runner: Function that should run the real binary
        sprefix: Prefix that should be used for commands.
        python: The python executable that should be used.
        name_filters:
            List of regex expressions that are used to filter the
            real project name. Make sure to include a match group named
            'name' in the regex, e.g.,
            [
                r'foo(?P<name>.)-flt'
            ]

    Returns: plumbum command, readty to launch.

    """
    env = __create_jinja_env()
    template = env.get_template('wrapping/run_dynamic.py.inc')

    name_absolute = os.path.abspath(name)
    real_f = name_absolute + PROJECT_BIN_F_EXT

    project_file = persist(project, suffix=".project")

    cfg_env = CFG['env'].value

    bin_path = list_to_path(cfg_env.get('PATH', []))
    bin_path = list_to_path([bin_path, os.environ["PATH"]])

    bin_lib_path = \
        list_to_path(cfg_env.get('LD_LIBRARY_PATH', []))
    bin_lib_path = \
        list_to_path([bin_lib_path, os.environ["LD_LIBRARY_PATH"]])
    home = cfg_env.get("HOME", os.getenv("HOME", ""))

    with open(name_absolute, 'w') as wrapper:
        wrapper.write(
            template.render(
                runf=strip_path_prefix(real_f, sprefix),
                project_file=strip_path_prefix(project_file, sprefix),
                path=str(bin_path),
                ld_library_path=str(bin_lib_path),
                home=str(home),
                python=python,
                name_filters=name_filters
            )
        )

    chmod("+x", name_absolute)
    return local[name_absolute]


def wrap_cc(
    filepath: str,
    compiler: BoundCommand,
    project: 'Project',
    python: str = sys.executable,
    detect_project: bool = False
) -> BoundCommand:
    """
    Substitute a compiler with a script that hides CFLAGS & LDFLAGS.

    This will generate a wrapper script in the current directory
    and return a complete plumbum command to it.

    Args:
        filepath (str): Path to the wrapper script.
        compiler (benchbuild.utils.cmd):
            Real compiler command we should call in the script.
        project (benchbuild.project.Project):
            The project this compiler will be for.
        python (str): Path to the python interpreter we should use.
        detect_project: Should we enable project detection or not.

    Returns (benchbuild.utils.cmd):
        Command of the new compiler we can call.
    """
    env = __create_jinja_env()
    template = env.get_template('wrapping/run_compiler.py.inc')

    cc_fname = local.path(filepath).with_suffix(".benchbuild.cc", depth=0)
    cc_f = persist(compiler, filename=cc_fname)

    project_file = persist(project, suffix=".project")

    with open(filepath, 'w') as wrapper:
        wrapper.write(
            template.render(
                cc_f=cc_f,
                project_file=project_file,
                python=python,
                detect_project=detect_project
            )
        )

    chmod("+x", filepath)
    LOG.debug(
        "Placed wrapper in: %s for compiler %s", local.path(filepath),
        str(compiler)
    )
    LOG.debug("Placed project in: %s", local.path(project_file))
    LOG.debug("Placed compiler command in: %s", local.path(cc_f))
    return local[filepath]


def persist(id_obj, filename=None, suffix=None):
    """Persist an object in the filesystem.

    This will generate a pickled version of the given obj in the filename path.
    Objects shall provide an id() method to be able to use this persistence API.
    If not, we will use the id() builtin of python to generate an identifier
    for you.

    The file will be created, if it does not exist.
    If the file already exists, we will overwrite it.

    Args:
        id_obj (Any): An identifiable object you want to persist in the
                      filesystem.
    """
    if suffix is None:
        suffix = ".pickle"
    if hasattr(id_obj, 'run_uuid'):
        ident = id_obj.run_uuid
    else:
        ident = str(id(id_obj))

    if filename is None:
        filename = "{obj_id}{suffix}".format(obj_id=ident, suffix=suffix)

    with open(filename, 'wb') as obj_file:
        dill.dump(id_obj, obj_file)
    return os.path.abspath(filename)


def load(filename: str) -> tp.Optional[tp.Any]:
    """Load a pickled obj from the filesystem.

    You better know what you expect from the given pickle, because we don't
    check it.

    Args:
        filename (str): The filename we load the object from.

    Returns:
        The object we were able to unpickle, else None.
    """
    if not os.path.exists(filename):
        LOG.error("load object - File '%s' does not exist.", filename)
        return None

    obj = None
    with open(filename, 'rb') as obj_file:
        obj = dill.load(obj_file)
    return obj
