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

import dill
from plumbum import local

from benchbuild.settings import CFG
from benchbuild.utils.cmd import chmod, mv
from benchbuild.utils.path import list_to_path
from benchbuild.utils.run import uchroot_no_llvm as uchroot
from benchbuild.utils.run import run

PROJECT_BIN_F_EXT = ".bin"
PROJECT_BLOB_F_EXT = ".postproc"
LOG = logging.getLogger(__name__)


def strip_path_prefix(ipath, prefix):
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
    if prefix is None:
        return ipath

    return ipath[len(prefix):] if ipath.startswith(prefix) else ipath


def unpickle(pickle_file):
    """Unpickle a python object from the given path."""
    pickle = None
    with open(pickle_file, "rb") as pickle_f:
        pickle = dill.load(pickle_f)
    if not pickle:
        LOG.error("Could not load python object from file")
    return pickle


def wrap(name, runner, sprefix=None, python=sys.executable):
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
    from jinja2 import Environment, PackageLoader
    env = Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        loader=PackageLoader('benchbuild', 'utils/templates')
    )
    template = env.get_template('run_static.py.inc')

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

    bin_path = list_to_path(CFG["env"]["path"].value())
    bin_path = list_to_path([bin_path, os.environ["PATH"]])

    bin_lib_path = list_to_path(CFG["env"]["ld_library_path"].value())
    bin_lib_path = list_to_path([bin_lib_path, os.environ["LD_LIBRARY_PATH"]])

    with open(name_absolute, 'w') as wrapper:
        wrapper.write(
            template.render(
                runf=strip_path_prefix(real_f, sprefix),
                blobf=strip_path_prefix(blob_f, sprefix),
                path=str(bin_path),
                ld_library_path=str(bin_lib_path),
                python=python,
            )
        )

    run(chmod["+x", name_absolute])
    return local[name_absolute]


def wrap_dynamic(self, name, runner,
                 sprefix=None,
                 python=sys.executable,
                 name_filters=None):
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
    from jinja2 import Environment, PackageLoader
    env = Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        loader=PackageLoader('benchbuild', 'utils/templates')
    )
    template = env.get_template('run_dynamic.py.inc')

    base_class = self.__class__.__name__
    base_module = self.__module__

    name_absolute = os.path.abspath(name)
    blob_f = name_absolute + PROJECT_BLOB_F_EXT
    real_f = name_absolute + PROJECT_BIN_F_EXT
    with open(blob_f, 'wb') as blob:
        blob.write(dill.dumps(runner))

    bin_path = list_to_path(CFG["env"]["path"].value())
    bin_path = list_to_path([bin_path, os.environ["PATH"]])

    bin_lib_path = \
        list_to_path(CFG["env"]["ld_library_path"].value())
    bin_lib_path = \
        list_to_path([bin_lib_path, os.environ["LD_LIBRARY_PATH"]])

    with open(name_absolute, 'w') as wrapper:
        wrapper.write(
            template.render(
                runf=strip_path_prefix(real_f, sprefix),
                blobf=strip_path_prefix(blob_f, sprefix),
                path=str(bin_path),
                base_class=base_class,
                base_module=base_module,
                ld_library_path=str(bin_lib_path),
                python=python,
                name_filters=name_filters
            )
        )

    chmod("+x", name_absolute)
    return local[name_absolute]


def wrap_cc(filepath, cflags, ldflags, compiler, extension,
            compiler_ext_name=None, python=sys.executable):
    """
    Substitute a compiler with a script that hides CFLAGS & LDFLAGS.

    This will generate a wrapper script in the current directory
    and return a complete plumbum command to it.

    Args:
        filepath (str): Path to the wrapper script.
        cflags (list(str)): The CFLAGS we want to hide.
        ldflags (list(str)): The LDFLAGS we want to hide.
        compiler (benchbuild.utils.cmd): Real compiler command we should call in the
            script.
        extension: A function that will be pickled alongside the compiler.
            It will be called before the actual compilation took place. This
            way you can intercept the compilation process with arbitrary python
            code.
        compiler_ext_name: The name that we should give to the generated
            dill blob for :func:

    Returns (benchbuild.utils.cmd):
        Command of the new compiler we can call.
    """
    from jinja2 import Environment, PackageLoader
    env = Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        loader=PackageLoader('benchbuild', 'utils/templates')
    )
    template = env.get_template('run_compiler.py.inc')

    cc_f = os.path.abspath(filepath + ".benchbuild.cc")
    with open(cc_f, 'wb') as compiler_pickle:
        compiler_pickle.write(dill.dumps(compiler()))
        if compiler_ext_name is not None:
            cc_f = compiler_ext_name(".benchbuild.cc")

    blob_f = os.path.abspath(filepath + PROJECT_BLOB_F_EXT)
    if extension is not None:
        with open(blob_f, 'wb') as blob:
            blob.write(dill.dumps(extension))
        if compiler_ext_name is not None:
            blob_f = compiler_ext_name(PROJECT_BLOB_F_EXT)

    # Update LDFLAGS with configure ld_library_path. This way
    # the libraries found in LD_LIBRARY_PATH are available at link-time too.
    lib_path_list = CFG["env"]["ld_library_path"].value()
    ldflags = ldflags + ["-L" + pelem for pelem in lib_path_list if pelem]

    with open(filepath, 'w') as wrapper:
        wrapper.write(
            template.render(
                cc_f=cc_f,
                blob_f=blob_f,
                cflags=cflags,
                ldflags=ldflags,
                python=python
            )
        )

    chmod("+x", filepath)
    LOG.debug("Placed wrapper in: {wrapper} for compiler {compiler}".format(
        wrapper=os.path.abspath(filepath),
        compiler=compiler()
    ))
    return local[filepath]


def wrap_in_uchroot(name, runner, sprefix=None):
    wrap(name, runner, sprefix, python="/usr/bin/env python3")


def wrap_dynamic_in_uchroot(self, name, runner, sprefix=None):
    wrap_dynamic(self, name, runner, sprefix, python="/usr/bin/env python3")
