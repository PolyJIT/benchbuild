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
from pathlib import Path

import dill
import plumbum as pb
from plumbum import local
from plumbum.commands.base import BoundCommand

from benchbuild.settings import CFG
from benchbuild.utils import run
from benchbuild.utils.cmd import chmod, mv
from benchbuild.utils.path import list_to_path
from benchbuild.utils.uchroot import no_llvm as uchroot

LOG = logging.getLogger(__name__)

# Configure default settings for dill pickle/unpickle, globally
dill.settings['ignore'] = True
dill.settings['recurse'] = True
dill.settings['protocol'] = -1
dill.settings['byref'] = True

if tp.TYPE_CHECKING:
    import jinja2

    import benchbuild.project.Project  # pylint: disable=unused-import


def strip_path_prefix(ipath: Path, prefix: Path) -> Path:
    """
    Strip prefix from path.

    Args:
        ipath: input path
        prefix: the prefix to remove, if it is found in :ipath:

    Examples:
        >>> strip_path_prefix(Path("/foo/bar"), Path("/bar"))
        PosixPath('/foo/bar')
        >>> strip_path_prefix(Path("/foo/bar"), Path("/"))
        PosixPath('/foo/bar')
        >>> strip_path_prefix(Path("/foo/bar"), Path("/foo"))
        PosixPath('/bar')
        >>> strip_path_prefix(Path("/foo/bar"), Path("None"))
        PosixPath('/foo/bar')

    """
    if prefix in ipath.parents:
        return Path("/") / ipath.relative_to(prefix)
    return ipath


def __create_jinja_env() -> 'jinja2.Environment':
    import jinja2  # pylint: disable=import-outside-toplevel
    return jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        loader=jinja2.PackageLoader("benchbuild", "res"),
    )


def wrap(
    name: str,
    project: "benchbuild.project.Project",
    sprefix: Path = Path(),
    python: str = sys.executable,
    bin_ext: str = ".bin",
) -> pb.commands.ConcreteCommand:
    """Wrap the binary :name: with the runtime extension of the project.

    This module generates a python tool that replaces :name:
    The function in runner only accepts the replaced binaries
    name as argument. We use the cloudpickle package to
    perform the serialization, make sure :runner: can be serialized
    with it and you're fine.

    Default behavior will remember wrapped paths and never move a remembered
    path to a binary location.

    Args:
        name: Binary we want to wrap
        project: The project that contains the runtime_extension we want
                 to run instead of the binary.

    Returns:
        A plumbum command, ready to launch.
    """
    env = __create_jinja_env()
    template = env.get_template("wrapping/run_static.py.inc")

    prefix = Path(sprefix)
    target = Path(name).absolute()
    if prefix in target.parents:
        _mv = run.watch(uchroot()["/bin/mv"])
    else:
        _mv = run.watch(mv)

    target = strip_path_prefix(target, prefix)
    real_path = strip_path_prefix(target.with_suffix(bin_ext), prefix)

    if target not in project:
        _mv(target, real_path)
        project.remember_path(target)

    project_file = persist(project, suffix=".project")

    env = CFG["env"].value

    collect_coverage = bool(CFG["coverage"]["collect"])
    coverage_config = str(CFG["coverage"]["config"])
    coverage_path = str(CFG["coverage"]["path"])

    bin_path = list_to_path(env.get("PATH", []))
    bin_path = list_to_path([bin_path, os.environ["PATH"]])

    bin_lib_path = list_to_path(env.get("LD_LIBRARY_PATH", []))
    bin_lib_path = list_to_path([bin_lib_path, os.environ["LD_LIBRARY_PATH"]])
    home = env.get("HOME", os.getenv("HOME", ""))

    with target.open("w") as wrapper:
        wrapper.write(
            template.render(
                runf=strip_path_prefix(real_path, prefix),
                project_file=strip_path_prefix(project_file, prefix),
                path=str(bin_path),
                ld_library_path=str(bin_lib_path),
                home=str(home),
                python=python,
                collect_coverage=collect_coverage,
                coverage_config=coverage_config,
                coverage_path=coverage_path
            )
        )

    _chmod = run.watch(chmod)
    _chmod("+x", str(target))
    return local[str(target)]


def wrap_dynamic(
    project: "benchbuild.project.Project",
    name: str,
    sprefix: Path = Path('.'),
    python: str = sys.executable,
    name_filters: tp.Optional[tp.List[str]] = None,
    bin_ext: str = ".bin",
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
    template = env.get_template("wrapping/run_dynamic.py.inc")

    prefix = Path(sprefix)
    target = Path(name).absolute()
    if prefix in target.parents:
        _mv = run.watch(uchroot()["/bin/mv"])
    else:
        _mv = run.watch(mv)

    target = strip_path_prefix(target, prefix)
    real_path = strip_path_prefix(target.with_suffix(bin_ext), prefix)

    if target not in project:
        _mv(target, real_path)

    project_file = persist(project, suffix=".project")

    cfg_env = CFG["env"].value
    collect_coverage = bool(CFG["coverage"]["collect"])
    coverage_config = str(CFG["coverage"]["config"])
    coverage_path = str(CFG["coverage"]["path"])

    bin_path = list_to_path(cfg_env.get("PATH", []))
    bin_path = list_to_path([bin_path, os.environ["PATH"]])

    bin_lib_path = list_to_path(cfg_env.get("LD_LIBRARY_PATH", []))
    bin_lib_path = list_to_path([bin_lib_path, os.environ["LD_LIBRARY_PATH"]])
    home = cfg_env.get("HOME", os.getenv("HOME", ""))

    with target.open("w") as wrapper:
        wrapper.write(
            template.render(
                runf=strip_path_prefix(real_path, prefix),
                project_file=strip_path_prefix(project_file, prefix),
                path=str(bin_path),
                ld_library_path=str(bin_lib_path),
                home=str(home),
                python=python,
                name_filters=name_filters,
                collect_coverage=collect_coverage,
                coverage_config=coverage_config,
                coverage_path=coverage_path
            )
        )

    chmod("+x", str(target))
    return local[str(target)]


def wrap_cc(
    filepath: str,
    compiler: BoundCommand,
    project: "benchbuild.project.Project",
    python: str = sys.executable,
    detect_project: bool = False,
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
    template = env.get_template("wrapping/run_compiler.py.inc")

    cc_fname = Path(filepath).with_suffix(".benchbuild.cc")
    cc_f = persist(compiler, filename=cc_fname)

    project_file = persist(project, suffix=".project")

    collect_coverage = bool(CFG["coverage"]["collect"])
    coverage_config = str(CFG["coverage"]["config"])
    coverage_path = str(CFG["coverage"]["path"])

    with open(filepath, "w") as wrapper:
        wrapper.write(
            template.render(
                cc_f=str(cc_f),
                project_file=str(project_file),
                python=python,
                detect_project=detect_project,
                collect_coverage=collect_coverage,
                coverage_config=coverage_config,
                coverage_path=coverage_path
            )
        )

    chmod("+x", filepath)
    LOG.debug("Placed wrapper in: %s for compiler %s", filepath, str(compiler))
    LOG.debug("Placed project in: %s", project_file)
    LOG.debug("Placed compiler command in: %s", cc_f)
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
    if hasattr(id_obj, "run_uuid"):
        ident = id_obj.run_uuid
    else:
        ident = str(id(id_obj))

    if filename is None:
        filename = f"{ident}{suffix}"

    with open(filename, "wb") as obj_file:
        dill.dump(id_obj, obj_file)
    return Path(filename).absolute()


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
    with open(filename, "rb") as obj_file:
        obj = dill.load(obj_file)
    return obj
