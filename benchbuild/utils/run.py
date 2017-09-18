"""Experiment helpers."""
import enum
import os
import logging
import subprocess
import typing as t
import sys
from contextlib import contextmanager

from benchbuild.settings import CFG
import benchbuild.signals as signals
from benchbuild.utils.cmd import mkdir
from benchbuild.utils.path import list_to_path
from benchbuild import settings
from plumbum import local, TEE
from plumbum.commands import ProcessExecutionError


LOG = logging.getLogger(__name__)


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


class RunInfo(object):
    def __begin(self, command, project, ename, group):
        """
        Begin a run in the database log.

        Args:
            command: The command that will be executed.
            pname: The project name we belong to.
            ename: The experiment name we belong to.
            group: The run group we belong to.

        Returns:
            (run, session), where run is the generated run instance and
            session the associated transaction for later use.
        """
        from benchbuild.utils.db import create_run
        from benchbuild.utils import schema as s
        from datetime import datetime

        db_run, session = create_run(command, project, ename, group)
        db_run.begin = datetime.now()
        db_run.status = 'running'
        log = s.RunLog()
        log.run_id = db_run.id
        log.begin = datetime.now()
        log.config = repr(CFG)
        session.add(log)
        session.add(db_run)

        self.db_run = db_run
        self.session = session

    def __end(self, stdout, stderr):
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

        run_id = self.db_run.id

        log = self.session.query(RunLog).filter(RunLog.run_id == run_id).one()
        log.stderr = stderr
        log.stdout = stdout
        log.status = 0
        log.end = datetime.now()

        self.db_run.end = datetime.now()
        self.db_run.status = 'completed'
        self.session.add(log)
        self.session.add(self.db_run)

    def __fail(self, retcode, stdout, stderr):
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
        run_id = self.db_run.id

        log = self.session.query(RunLog).filter(RunLog.run_id == run_id).one()
        log.stderr = stderr
        log.stdout = stdout
        log.status = retcode
        log.end = datetime.now()

        self.db_run.end = datetime.now()
        self.db_run.status = 'failed'
        self.session.add(log)
        self.session.add(self.db_run)

    def __init__(self, **kwargs):
        self.cmd = None
        self.project = None
        self.experiment = None
        self.retcode = 0
        self.stdout = []
        self.stderr = []

        for k in kwargs:
            self.__setattr__(k, kwargs[k])
        # This is not atomic, careful!
        self.__begin(self.cmd, self.project,
                     self.experiment.name, self.project.run_uuid)
        signals.handlers.register(self.__fail, 15, "SIGTERM", "SIGTERM")

        run_id = self.db_run.id
        settings.CFG["db"]["run_id"] = run_id

    def __add__(self, rhs):
        if rhs is None:
            return self

        r = RunInfo(
            retcode=self.retcode + rhs.retcode,
            stdout=self.stdout + rhs.stdout,
            stderr=self.stderr + rhs.stderr,
            db_run=[self.db_run, rhs.db_run],
            session=self.session)
        return r

    def __call__(self, *args, expected_retcode=0, ri=None, **kwargs):
        cmd_env = settings.to_env_dict(settings.CFG)

        with local.env(**cmd_env):
            try:
                LOG.debug("Command has input via stdin")
                bin_name = sys.argv[0]
                retcode, stdout, stderr = \
                    self.cmd & TEE(retcode=expected_retcode)
                f_stdout = bin_name + ".stdout"
                with open(f_stdout, 'w') as fd_stdout:
                    LOG.debug("stdout goes to: %s", f_stdout)
                    fd_stdout.write(stdout)

                f_stderr = bin_name + ".stderr"
                with open(f_stderr, 'w') as fd_stderr:
                    LOG.debug("stderr goes to: %s", f_stderr)
                    fd_stderr.write(stderr)

                self.retcode = retcode
                self.stdout = stdout
                self.stderr = stderr
                self.__end(str(stdout), str(stderr))
            except ProcessExecutionError as ex:
                self.__fail(ex.retcode, ex.stderr, ex.stdout)
                self.retcode = ex.retcode
                self.stdout = ex.stdout
                self.stderr = ex.stderr

                LOG.debug("Tracked process failed")
                LOG.error(str(ex))
            except KeyboardInterrupt:
                self.retcode = retcode
                self.stdout = stdout
                self.stderr = stderr
                self.__fail(-1, "", "KeyboardInterrupt")
                LOG.warning("Interrupted by user input")
                raise
            finally:
                signals.handlers.deregister(self.__fail,
                                            15, "SIGTERM", "SIGTERM")

        return self

    def commit(self):
        self.session.commit()

    def __str__(self):
        return "<RunInfo (ec={}, run_id={}, stdout={}, stderr={})>".format(
            self.retcode, self.db_run.id, len(self.stdout), len(self.stderr))

    def __repr__(self):
        return str(self)


def exit_code_from_run_infos(run_infos: t.List[RunInfo]):
    assert(run_infos is not None)

    if not hasattr(run_infos, "__iter__"):
        return run_infos.retcode

    rcs = [ri.retcode for ri in run_infos]
    max_rc = max(rcs)
    min_rc = min(rcs)
    if max_rc == 0:
        return min_rc
    return max_rc


@contextmanager
def track_execution(cmd, project, experiment, **kwargs):
    """
    Guard the execution of the given command.

    Args:
        cmd: the command we guard.
        pname: the database we run under.
        ename: the database session this run belongs to.
        run_group: the run group this execution will belong to.

    Raises:
        RunException: If the ``cmd`` encounters an error we wrap the exception
            in a RunException and re-raise. This ends the run unsuccessfully.
    """
    runner = RunInfo(cmd=cmd, project=project, experiment=experiment, **kwargs)
    yield runner
    runner.commit()


def run(command, retcode=0):
    """
    Execute a plumbum command, depending on the user's settings.

    Args:
    command & TEE(retcode=retcode)
        command: The plumbumb command to execute.
    """
    return command & TEE(retcode=retcode)


class UchrootEC(enum.Enum):
    MNT_FAILED = 255
    MNT_PROC_FAILED = 254
    MNT_DEV_FAILED = 253
    MNT_SYS_FAILED = 252
    MNT_PTS_FAILED = 251


def retry(pb_cmd, retries=0, max_retries=10, retcode=0, retry_retcodes=None):
    try:
        run(pb_cmd, retcode)
    except ProcessExecutionError as proc_ex:
        new_retcode = proc_ex.retcode
        if retries > max_retries:
            LOG.error("Retried %d times. No change. Abort", retries)
            raise

        if new_retcode in retry_retcodes:
            retry(pb_cmd, retries=retries+1,
                  max_retries=max_retries,
                  retcode=retcode,
                  retry_retcodes=retry_retcodes)
        else:
            raise

def uretry(cmd, retcode=0):
    retry(cmd, retcode=retcode, retry_retcodes=[
        UchrootEC.MNT_PROC_FAILED.value,
        UchrootEC.MNT_DEV_FAILED.value,
        UchrootEC.MNT_SYS_FAILED.value,
        UchrootEC.MNT_PTS_FAILED.value
    ])

def uchroot_no_args():
    """Return the uchroot command without any customizations."""
    from benchbuild.utils.cmd import uchroot

    prefixes = CFG["container"]["prefixes"].value()
    p_paths, p_libs = uchroot_env(prefixes)

    uchroot = with_env_recursive(
        uchroot,
        LD_LIBRARY_PATH=list_to_path(p_libs),
        PATH=list_to_path(p_paths))


    return uchroot


def uchroot_no_llvm(*args, **kwargs):
    """
    Return a customizable uchroot command.

    The command will be executed inside a uchroot environment.

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
    """
    Compute the mountpoints of the current user.

    Args:
        prefix: Define where the job was running if it ran on a cluster.
        mounts: All mounts the user currently uses in his file system.
    Return:
        mntpoints
    """
    i = 0
    mntpoints = []
    for mount in mounts:
        if not isinstance(mount, dict):
            mntpoint = "{0}/{1}".format(prefix, str(i))
            mntpoints.append(mntpoint)
            i = i + 1
    return mntpoints


def _uchroot_mounts(prefix, mounts, uchroot):
    i = 0
    new_uchroot = uchroot
    mntpoints = []
    for mount in mounts:
        src_mount = mount
        if isinstance(mount, dict):
            src_mount = mount["src"]
            tgt_mount = mount["tgt"]
        else:
            tgt_mount = "{0}/{1}".format(prefix, str(i))
            i = i + 1
        mkdir("-p", tgt_mount)
        new_uchroot = new_uchroot["-M", "{0}:/{1}".format(src_mount, tgt_mount)]
        mntpoints.append(tgt_mount)
    return new_uchroot, mntpoints


def uchroot_env(mounts):
    """
    Compute the environment of the change root for the user.

    Args:
        mounts: The mountpoints of the current user.
    Return:
        paths
        ld_libs
    """
    f_mounts = [m.strip("/") for m in mounts]

    ld_libs = ["/{0}/lib".format(m) for m in f_mounts]
    ld_libs.extend(["/{0}/lib64".format(m) for m in f_mounts])

    paths = ["/{0}/bin".format(m) for m in f_mounts]
    paths.extend(["/{0}/sbin".format(m) for m in f_mounts])
    paths.extend(["/{0}".format(m) for m in f_mounts])
    return paths, ld_libs


def with_env_recursive(cmd, **envvars):
    """
    Recursively updates the environment of cmd and all its subcommands.

    Args:
        cmd - A plumbum command-like object
        **envvars - The environment variables to update

    Returns:
        The updated command.
    """
    from plumbum.commands.base import BoundCommand, BoundEnvCommand
    if isinstance(cmd, BoundCommand):
        cmd.cmd = with_env_recursive(cmd.cmd, **envvars)
    elif isinstance(cmd, BoundEnvCommand):
        cmd.envvars.update(envvars)
        cmd.cmd = with_env_recursive(cmd.cmd, **envvars)
    return cmd


def uchroot_with_mounts(*args, **kwargs):
    """Return a uchroot command with all mounts enabled."""
    uchroot_cmd = uchroot_no_args(*args, **kwargs)
    uchroot_cmd, mounts = \
        _uchroot_mounts("mnt", CFG["container"]["mounts"].value(), uchroot_cmd)
    paths, libs = uchroot_env(mounts)

    prefixes = CFG["container"]["prefixes"].value()
    p_paths, p_libs = uchroot_env(prefixes)

    uchroot_cmd = with_env_recursive(
        uchroot_cmd,
        LD_LIBRARY_PATH=list_to_path(libs+p_libs),
        PATH=list_to_path(paths+p_paths))
    return uchroot_cmd


def uchroot(*args, **kwargs):
    """
    Return a customizable uchroot command.

    Args:
        args: List of additional arguments for uchroot (typical: mounts)
    Return:
        chroot_cmd
    """
    mkdir("-p", "llvm")
    uchroot_cmd = uchroot_no_llvm(*args, **kwargs)
    uchroot_cmd, mounts = _uchroot_mounts(
        "mnt", CFG["container"]["mounts"].value(), uchroot_cmd)
    paths, libs = uchroot_env(mounts)
    p_paths, p_libs = uchroot_env(CFG["container"]["prefixes"].value())

    uchroot_cmd = uchroot_cmd.with_env(
        LD_LIBRARY_PATH=list_to_path(libs + p_libs),
        PATH=list_to_path(paths + p_paths))
    return uchroot_cmd["--"]


def in_builddir(sub='.'):
    """
    Decorate a project phase with a local working directory change.

    Args:
        sub: An optional subdirectory to change into.
    """
    from functools import wraps
    from os import path

    def wrap_in_builddir(func):
        """Wrap the function for the new build directory."""
        @wraps(func)
        def wrap_in_builddir_func(self, *args, **kwargs):
            """The actual function inside the wrapper for the new builddir."""
            p = path.abspath(path.join(self.builddir, sub))
            try:
                with local.cwd(p):
                    return func(self, *args, **kwargs)
            except FileNotFoundError:
                LOG.debug("Chdir to %s failed. Directory does not exist.", p)

        return wrap_in_builddir_func

    return wrap_in_builddir


def unionfs_set_up(ro_base, rw_image, mountpoint):
    """
    Setup a unionfs via unionfs-fuse.

    Args:
        ro_base: base_directory of the project
        rw_image: virtual image of actual file system
        mountpoint: location where ro_base and rw_image merge
    """
    if not os.path.exists(mountpoint):
        mkdir("-p", mountpoint)
    if not os.path.exists(ro_base):
        LOG.error("Base dir does not exist: '%s'", ro_base)
        raise ValueError("Base directory does not exist")
    if not os.path.exists(rw_image):
        LOG.error("Image dir does not exist: '%s'", ro_base)
        raise ValueError("Image directory does not exist")

    from benchbuild.utils.cmd import unionfs
    ro_base = os.path.abspath(ro_base)
    rw_image = os.path.abspath(rw_image)
    mountpoint = os.path.abspath(mountpoint)
    return unionfs["-f", "-o", "auto_unmount,allow_other,cow",
                   rw_image + "=RW:" + ro_base + "=RO", mountpoint]


def unionfs_is_active(root):
    import psutil

    real_root = os.path.realpath(root)
    for part in psutil.disk_partitions(all=True):
        if os.path.commonpath([part.mountpoint, real_root]) == real_root:
            if part.fstype in ["fuse.unionfs", "fuse.unionfs-fuse"]:
                return True
    return False


class UnmountError(BaseException):
    pass


def unionfs(base_dir='./base',
            image_dir='./image',
            image_prefix=None,
            mountpoint='./union'):
    """
    Decorator for the UnionFS feature.

    This configures a unionfs for projects. The given base_dir and/or image_dir
    are layered as follows:
     image_dir=RW:base_dir=RO
    All writes go to the image_dir, while base_dir delivers the (read-only)
    versions of the rest of the filesystem.

    The unified version will be provided in the project's builddir. Unmouting
    is done as soon as the function completes.

    Args:
        base_dir:The unpacked container of a project delievered by a method
                 out of the container utils.
        image_dir: Virtual image of the actual file system represented by the
                   build_dir of a project.
        image_prefix: Useful prefix if the projects run on a cluster,
                      to identify where the job came from and where it runs.
        mountpoint: Location where the filesystems merge, currently per default
                    as './union'.
    """
    from functools import wraps

    def update_cleanup_paths(new_path):
        """
        Add the new path to the list of paths to clean up afterwards.

        Args:
            new_path: Path to the directory that need to be cleaned up.
        """
        cleanup_dirs = settings.CFG["cleanup_paths"].value()
        cleanup_dirs = set(cleanup_dirs)
        cleanup_dirs.add(new_path)
        cleanup_dirs = list(cleanup_dirs)
        settings.CFG["cleanup_paths"] = cleanup_dirs

    def is_outside_of_builddir(project, path_to_check):
        """Check if a project lies outside of its expected directory."""
        bdir = project.builddir
        cprefix = os.path.commonprefix([path_to_check, bdir])
        return cprefix != bdir

    def wrap_in_union_fs(func):
        """
        Function that wraps a given function inside the file system.

        Args:
            func: The function that needs to be wrapped inside the unions fs.
        Return:
            The file system with the function wrapped inside.
        """
        nonlocal image_prefix

        @wraps(func)
        def wrap_in_union_fs_func(project, *args, **kwargs):
            """
            Wrap the func in the UnionFS mount stack.

            We make sure that the mount points all exist and stack up the
            directories for the unionfs. All directories outside of the default
            build environment are tracked for deletion.
            """
            container = project.container
            abs_base_dir = os.path.abspath(container.local)
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

            unionfs_cmd = unionfs_set_up(
                abs_base_dir, abs_image_dir, abs_mount_dir)
            project_builddir_bak = project.builddir
            project.builddir = abs_mount_dir
            project.setup_derived_filenames()

            proc = unionfs_cmd.popen()
            while (not unionfs_is_active(root=abs_mount_dir)) and \
                  (proc.poll() is None):
                pass

            ret = None
            if proc.poll() is None:
                try:
                    with local.cwd(abs_mount_dir):
                        ret = func(project, *args, **kwargs)
                finally:
                    project.builddir = project_builddir_bak
                    project.setup_derived_filenames()

                    from signal import SIGINT
                    is_running = proc.poll() is None
                    while unionfs_is_active(root=abs_mount_dir) and is_running:
                        try:
                            proc.send_signal(SIGINT)
                            proc.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                            is_running = False
                    LOG.debug("Unionfs shut down.")

            if unionfs_is_active(root=abs_mount_dir):
                raise UnmountError()

            return ret

        return wrap_in_union_fs_func

    return wrap_in_union_fs


def store_config(func):
    """Decorator for storing the configuration in the project's builddir."""
    from functools import wraps

    @wraps(func)
    def wrap_store_config(self, *args, **kwargs):
        """Wrapper that contains the actual storage call for the config."""
        p = os.path.abspath(os.path.join(self.builddir))
        CFG.store(os.path.join(p, ".benchbuild.yml"))
        return func(self, *args, **kwargs)

    return wrap_store_config
