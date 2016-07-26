"""
Experiment helpers
"""
import os
from benchbuild.utils.cmd import mkdir  # pylint: disable=E0401
from benchbuild.utils.path import list_to_path
from contextlib import contextmanager
from types import SimpleNamespace
from benchbuild import settings
import logging


def partial(func, *args, **kwargs):
    """
    Partial function application.

    This performs standard partial application on the given function. However,
    we do not check if parameter values in args and kwargs collide with each
    other.

    Args:
        func: The original function.
        *args: Positional arguments that should be applied partially.
        **kwargs: Keyword arguments that should be applied partially.

    Returns:
        A new function that has all given args and kwargs bound.
    """
    frozen_args = args
    frozen_kwargs = kwargs

    def partial_func(*args, **kwargs):
        """ The partial function with pre-bound arguments. """
        nonlocal frozen_args
        nonlocal frozen_kwargs
        nonlocal func
        thawed_args = frozen_args + args
        thawed_kwargs = frozen_kwargs.copy()
        thawed_kwargs.update(kwargs)
        func(*thawed_args, **thawed_kwargs)

    return partial_func


def handle_stdin(cmd, kwargs):
    """
    Handle stdin for wrapped runtime executors.

    This little helper checks the kwargs for a `has_stdin` key containing
    a boolean value. If necessary it will pipe in the stdin of this process
    into the plumbum command.

    Args:
        cmd (benchbuild.utils.cmd): Command to wrap a stdin handler around.
        kwargs: Dictionary containing the kwargs.
            We check for they key `has_stdin`

    Returns:
        A new plumbum command that deals with stdin redirection, if needed.
    """
    assert isinstance(kwargs, dict)
    import sys

    has_stdin = kwargs.get("has_stdin", False)
    if has_stdin:
        run_cmd = (cmd < sys.stdin)
    else:
        run_cmd = cmd

    return run_cmd


def fetch_time_output(marker, format_s, ins):
    """
    Fetch the output /usr/bin/time from a.

    Args:
        marker: The marker that limits the time output
        format_s: The format string used to parse the timings
        ins: A list of lines we look for the output.

    Returns:
        A list of timing tuples
    """
    from parse import parse

    timings = [x for x in ins if marker in x]
    res = [parse(format_s, t) for t in timings]
    return [_f for _f in res if _f]


class GuardedRunException(Exception):
    """
    BB Run exception.

    Contains an exception that ocurred during execution of a benchbuild
    experiment.
    """

    def __init__(self, what, db_run, session):
        """
        Exception raised when a binary failed to execute properly.

        Args:
            what: the original exception.
            run: the run during which we encountered ``what``.
            session: the db session we want to log to.
        """
        super(GuardedRunException, self).__init__()

        self.what = what
        self.run = db_run

        if isinstance(what, KeyboardInterrupt):
            session.rollback()

    def __str__(self):
        return self.what.__str__()

    def __repr__(self):
        return self.what.__repr__()


def begin_run_group(project):
    """
    Begin a run_group in the database.

    A run_group groups a set of runs for a given project. This models a series
    of runs that form a complete binary runtime test.

    Args:
        project: The project we begin a new run_group for.

    Returns:
        ``(group, session)`` where group is the created group in the
        database and session is the database session this group lives in.
    """
    from benchbuild.utils.db import create_run_group
    from datetime import datetime

    group, session = create_run_group(project)
    group.begin = datetime.now()
    group.status = 'running'

    session.commit()
    return group, session


def end_run_group(group, session):
    """
    End the run_group successfully.

    Args:
        group: The run_group we want to complete.
        session: The database transaction we will finish.
    """
    from datetime import datetime

    group.end = datetime.now()
    group.status = 'completed'
    session.commit()


def fail_run_group(group, session):
    """
    End the run_group unsuccessfully.

    Args:
        group: The run_group we want to complete.
        session: The database transaction we will finish.
    """
    from datetime import datetime

    group.end = datetime.now()
    group.status = 'failed'
    session.commit()


def begin(command, pname, ename, group):
    """
    Begin a run in the database log.

    Args:
        command: The command that will be executed.
        pname: The project name we belong to.
        ename: The experiment name we belong to.
        group: The run group we belong to.

    Returns:
        (run, session), where run is the generated run instance and session the
        associated transaction for later use.
    """
    from benchbuild.utils.db import create_run
    from benchbuild.utils import schema as s
    from benchbuild.settings import CFG
    from datetime import datetime

    db_run, session = create_run(command, pname, ename, group)
    db_run.begin = datetime.now()
    db_run.status = 'running'
    log = s.RunLog()
    log.run_id = db_run.id
    log.begin = datetime.now()
    log.config = repr(CFG)

    session.add(log)
    session.commit()

    return db_run, session


def end(db_run, session, stdout, stderr):
    """
    End a run in the database log (Successfully).

    This will persist the log information in the database and commit the
    transaction.

    Args:
        db_run: The ``run`` schema object we belong to
        session: The db transaction we belong to.
        stdout: The stdout we captured of the run.
        stderr: The stderr we capture of the run.
    """
    from benchbuild.utils.schema import RunLog
    from datetime import datetime
    log = session.query(RunLog).filter(RunLog.run_id == db_run.id).one()
    log.stderr = stderr
    log.stdout = stdout
    log.status = 0
    log.end = datetime.now()
    db_run.end = datetime.now()
    db_run.status = 'completed'
    session.add(log)
    session.commit()


def fail(db_run, session, retcode, stdout, stderr):
    """
    End a run in the database log (Unsuccessfully).

    This will persist the log information in the database and commit the
    transaction.

    Args:
        db_run: The ``run`` schema object we belong to
        session: The db transaction we belong to.
        retcode: The return code we captured of the run.
        stdout: The stdout we captured of the run.
        stderr: The stderr we capture of the run.
    """
    from benchbuild.utils.schema import RunLog
    from datetime import datetime
    log = session.query(RunLog).filter(RunLog.run_id == db_run.id).one()
    log.stderr = stderr
    log.stdout = stdout
    log.status = retcode
    log.end = datetime.now()
    db_run.end = datetime.now()
    db_run.status = 'failed'
    session.add(log)
    session.commit()


@contextmanager
def guarded_exec(cmd, project, experiment):
    """
    Guard the execution of the given command.

    Args:
        cmd: the command we guard.
        pname: the database run we run under.
        ename: the database session this run belongs to.
        run_group: the run group this execution will belong to.

    Raises:
        RunException: If the ``cmd`` encounters an error we wrap the exception
            in a RunException and re-raise. This ends the run unsuccessfully.
    """
    from plumbum.commands import ProcessExecutionError
    from plumbum import local
    from plumbum.commands.modifiers import TEE
    from warnings import warn

    db_run, session = begin(cmd, project.name, experiment.name,
                            project.run_uuid)
    ex = None
    with local.env(BB_DB_RUN_ID=db_run.id):

        def runner(retcode=0, *args):
            retcode, stdout, stderr = cmd[args] & TEE(retcode=retcode)
            end(db_run, session, stdout, stderr)
            r = SimpleNamespace()
            r.retcode = retcode
            r.stdout = stdout
            r.stderr = stderr
            r.session = session
            r.db_run = db_run
            return r

        try:
            yield runner
        except KeyboardInterrupt:
            fail(db_run, session, -1, "", "KeyboardInterrupt")
            warn("Interrupted by user input")
            raise
        except ProcessExecutionError as proc_ex:
            fail(db_run, session, proc_ex.retcode, proc_ex.stdout,
                 proc_ex.stderr)
            raise
        except Exception as ex:
            fail(db_run, session, -1, "", str(ex))
            raise


def run(command, retcode=0):
    """
    Execute a plumbum command, depending on the user's settings.

    Args:
        command: The plumbumb command to execute.
    """
    from logging import info
    from plumbum.commands.modifiers import TEE
    info(str(command))
    command & TEE(retcode)


def uchroot_no_args():
    """Return the uchroot command without any customizations."""
    from benchbuild.utils.cmd import uchroot

    return uchroot


def uchroot_no_llvm(*args, **kwargs):
    """
    Returns a uchroot command which can be called with other args to be
            executed in the uchroot.
    Args:
        args: List of additional arguments for uchroot (typical: mounts)
    Return:
        chroot_cmd
    """
    uid = kwargs.pop('uid', 0)
    gid = kwargs.pop('gid', 0)

    uchroot_cmd = uchroot_no_args()
    uchroot_cmd = uchroot_cmd["-C", "-w", "/", "-r", os.path.abspath(".")]
    uchroot_cmd = uchroot_cmd["-u", str(uid), "-g", str(gid), "-E", "-A"]
    return uchroot_cmd[args]


def uchroot_mounts(prefix, mounts):
    i = 0
    mntpoints = []
    for mount in mounts:
        mntpoint = "{0}/{1}".format(prefix, str(i))
        mntpoints.append(mntpoint)
        i = i + 1
    return mntpoints


def _uchroot_mounts(prefix, mounts, uchroot):
    i = 0
    new_uchroot = uchroot
    mntpoints = []
    for mount in mounts:
        mntpoint = "{0}/{1}".format(prefix, str(i))
        mkdir("-p", mntpoint)
        new_uchroot = new_uchroot["-M", "{0}:/{1}".format(mount, mntpoint)]
        mntpoints.append(mntpoint)
        i = i + 1
    return new_uchroot, mntpoints


def uchroot_env(mounts):
    import logging as l
    ld_libs = ["/{0}/lib".format(m) for m in mounts]
    paths = ["/{0}/bin".format(m) for m in mounts]
    paths.extend(["/{0}".format(m) for m in mounts])
    paths.extend(["/usr/bin", "/bin", "/usr/sbin", "/sbin"])
    return paths, ld_libs


def uchroot(*args, **kwargs):
    """
    Returns a uchroot command which can be called with other args to be
            executed in the uchroot.
    Args:
        args: List of additional arguments for uchroot (typical: mounts)
    Return:
        chroot_cmd
    """
    from benchbuild.settings import CFG
    mkdir("-p", "llvm")
    uchroot_cmd = uchroot_no_llvm(*args, **kwargs)
    uchroot_cmd, mounts = \
            _uchroot_mounts("mnt", CFG["uchroot"]["mounts"].value(),
                            uchroot_cmd)
    paths, libs = uchroot_env(mounts)
    uchroot_cmd = uchroot_cmd.with_env(
            LD_LIBRARY_PATH=list_to_path(libs),
            PATH=list_to_path(paths))
    return uchroot_cmd["--"]


def in_builddir(sub='.'):
    """
    Decorate a project phase with a local working directory change.

    Args:
        sub: An optional subdirectory to change into.
    """
    from functools import wraps
    from plumbum import local
    from os import path

    def wrap_in_builddir(func):
        @wraps(func)
        def wrap_in_builddir_func(self, *args, **kwargs):
            p = path.abspath(path.join(self.builddir, sub))
            with local.cwd(p):
                return func(self, *args, **kwargs)

        return wrap_in_builddir_func

    return wrap_in_builddir


def unionfs_tear_down(mountpoint, tries=3):
    """
    Tear down a unionfs mountpoint.
    """
    from benchbuild.utils.cmd import fusermount, sync
    log = logging.getLogger("benchbuild")

    if not os.path.exists(mountpoint):
        log.error("Mountpoint does not exist: '{0}'".format(mountpoint))
        raise ValueError("Mountpoint does not exist: '{0}'".format(mountpoint))

    fusermount("-u", mountpoint, retcode=None)
    if os.path.ismount(mountpoint):
        sync()
        if tries > 0:
            unionfs_tear_down(mountpoint, tries=tries - 1)
        else:
            log.error("Failed to unmount '{0}'".format(mountpoint))
            raise RuntimeError("Failed to unmount '{0}'".format(mountpoint))


def unionfs_set_up(ro_base, rw_image, mountpoint):
    """
    Setup a unionfs via unionfs-fuse.

    Args:
        ro_base:
        rw_image:
        mountpoint:
    """
    log = logging.getLogger("benchbuild")
    if not os.path.exists(mountpoint):
        mkdir("-p", mountpoint)
    if not os.path.exists(ro_base):
        log.error("Base dir does not exist: '{0}'".format(ro_base))
        raise ValueError("Base directory does not exist")
    if not os.path.exists(rw_image):
        log.error("Image dir does not exist: '{0}'".format(ro_base))
        raise ValueError("Image directory does not exist")

    from benchbuild.utils.cmd import unionfs
    ro_base = os.path.abspath(ro_base)
    rw_image = os.path.abspath(rw_image)
    mountpoint = os.path.abspath(mountpoint)
    unionfs("-o", "allow_other,cow", rw_image + "=RW:" + ro_base + "=RO",
            mountpoint)


def unionfs(base_dir='./base',
            image_dir='./image',
            image_prefix=None,
            mountpoint='./union'):
    """
    UnionFS decorator.

    This configures a unionfs for projects. The given base_dir and/or image_dir
    are layered as follows:
     image_dir=RW:base_dir=RO
    All writes go to the image_dir, while base_dir delivers the (read-only)
    versions of the rest of the filesystem.

    The unified version will be provided in the project's builddir. Unmouting
    is done as soon as the function completes.

    Args:
        base_dir:
        image_dir:
        image_prefix:
        mountpoint:
    """
    from functools import wraps
    from plumbum import local

    def update_cleanup_paths(new_path):
        cleanup_dirs = settings.CFG["cleanup_paths"].value()
        cleanup_dirs = set(cleanup_dirs)
        cleanup_dirs.add(new_path)
        cleanup_dirs = list(cleanup_dirs)
        settings.CFG["cleanup_paths"] = cleanup_dirs

    def is_outside_of_builddir(project, path_to_check):
        bdir = project.builddir
        cprefix = os.path.commonprefix([path_to_check, bdir])
        return cprefix != bdir

    def wrap_in_union_fs(func):
        nonlocal image_prefix

        @wraps(func)
        def wrap_in_union_fs_func(project, *args, **kwargs):
            abs_base_dir = os.path.abspath(os.path.join(project.builddir,
                                                        base_dir))
            nonlocal image_prefix
            if image_prefix is not None:
                image_prefix = os.path.abspath(image_prefix)
                rel_prj_builddir = os.path.relpath(
                    project.builddir, settings.CFG["build_dir"].value())
                abs_image_dir = os.path.abspath(os.path.join(
                    image_prefix, rel_prj_builddir, image_dir))

                if is_outside_of_builddir:
                    update_cleanup_paths(abs_image_dir)
            else:
                abs_image_dir = os.path.abspath(os.path.join(project.builddir,
                                                             image_dir))
            abs_mount_dir = os.path.abspath(os.path.join(project.builddir,
                                                         mountpoint))
            if not os.path.exists(abs_base_dir):
                mkdir("-p", abs_base_dir)
            if not os.path.exists(abs_image_dir):
                mkdir("-p", abs_image_dir)
            if not os.path.exists(abs_mount_dir):
                mkdir("-p", abs_mount_dir)

            unionfs_set_up(abs_base_dir, abs_image_dir, abs_mount_dir)
            project_builddir_bak = project.builddir
            project.builddir = abs_mount_dir
            project.setup_derived_filenames()
            try:
                with local.cwd(abs_mount_dir):
                    ret = func(project, *args, **kwargs)
            finally:
                unionfs_tear_down(abs_mount_dir)
            project.builddir = project_builddir_bak
            project.setup_derived_filenames()
            return ret

        return wrap_in_union_fs_func

    return wrap_in_union_fs
