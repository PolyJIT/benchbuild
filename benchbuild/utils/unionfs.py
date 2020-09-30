import functools
import logging
import os
import signal
import subprocess

import psutil
from plumbum import local

from benchbuild import settings
from benchbuild.utils.container import in_container

LOG = logging.getLogger(__name__)


def unionfs(rw='rw', ro=None, union='union'):
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
        rw: writeable storage area for the unified fuse filesystem.
        ro: read-only storage area for the unified fuse filesystem.
        union: mountpoint of the unified fuse filesystem.
    """
    del ro

    def wrap_in_union_fs(func):
        """
        Function that wraps a given function inside the file system.

        Args:
            func: The function that needs to be wrapped inside the unions fs.
        Return:
            The file system with the function wrapped inside.
        """

        @functools.wraps(func)
        def wrap_in_union_fs_func(project, *args, **kwargs):
            """
            Wrap the func in the UnionFS mount stack.

            We make sure that the mount points all exist and stack up the
            directories for the unionfs. All directories outside of the default
            build environment are tracked for deletion.
            """
            container = project.container
            if container is None or in_container():
                return func(project, *args, **kwargs)

            build_dir = local.path(project.builddir)
            LOG.debug("UnionFS - Project builddir: %s", project.builddir)
            if __unionfs_is_active(root=build_dir):
                LOG.debug(
                    "UnionFS already active in %s, nesting not supported.",
                    build_dir
                )
                return func(project, *args, **kwargs)

            ro_dir = local.path(container.local)
            rw_dir = build_dir / rw
            un_dir = build_dir / union
            LOG.debug("UnionFS - RW: %s", rw_dir)

            unionfs_cmd = __unionfs_set_up(ro_dir, rw_dir, un_dir)
            project_builddir_bak = project.builddir
            project.builddir = un_dir

            proc = unionfs_cmd.popen()
            while (not __unionfs_is_active(root=un_dir)) and \
                  (proc.poll() is None):
                pass

            ret = None
            if proc.poll() is None:
                try:
                    with local.cwd(un_dir):
                        ret = func(project, *args, **kwargs)
                finally:
                    project.builddir = project_builddir_bak

                    is_running = proc.poll() is None
                    while __unionfs_is_active(root=un_dir) and is_running:
                        try:
                            proc.send_signal(signal.SIGINT)
                            proc.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                            is_running = False
                    LOG.debug("Unionfs shut down.")

            if __unionfs_is_active(root=un_dir):
                raise UnmountError()

            return ret

        return wrap_in_union_fs_func

    return wrap_in_union_fs


def __update_cleanup_paths(new_path):
    """
    Add the new path to the list of paths to clean up afterwards.

    Args:
        new_path: Path to the directory that need to be cleaned up.
    """
    cleanup_dirs = settings.CFG["cleanup_paths"].value
    cleanup_dirs = set(cleanup_dirs)
    cleanup_dirs.add(new_path)
    cleanup_dirs = list(cleanup_dirs)
    settings.CFG["cleanup_paths"] = cleanup_dirs


def __is_outside_of_builddir(project, path_to_check):
    """Check if a project lies outside of its expected directory."""
    bdir = project.builddir
    cprefix = os.path.commonprefix([path_to_check, bdir])
    return cprefix != bdir


def __unionfs_is_active(root):
    real_root = os.path.realpath(root)
    for part in psutil.disk_partitions(all=True):
        if os.path.commonpath([part.mountpoint, real_root]) == real_root:
            if part.fstype in ["fuse.unionfs", "fuse.unionfs-fuse"]:
                return True
    return False


def __unionfs_set_up(ro_dir, rw_dir, mount_dir):
    """
    Setup a unionfs via unionfs-fuse.

    Args:
        ro_base: base_directory of the project
        rw_image: virtual image of actual file system
        mountpoint: location where ro_base and rw_image merge
    """
    mount_dir.mkdir()
    rw_dir.mkdir()
    if not ro_dir.exists():
        LOG.error("Base dir does not exist: '%s'", ro_dir)
        raise ValueError("Base directory does not exist")

    from benchbuild.utils.cmd import unionfs as unionfs_cmd
    LOG.debug(
        "Mounting UnionFS on %s with RO:%s RW:%s", mount_dir, ro_dir, rw_dir
    )
    return unionfs_cmd["-f", "-o", "auto_unmount,allow_other,cow",
                       rw_dir + "=RW:" + ro_dir + "=RO", mount_dir]


class UnmountError(BaseException):
    pass
