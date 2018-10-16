import logging
import os
import subprocess

import psutil
from plumbum import local

from benchbuild import settings

LOG = logging.getLogger(__name__)


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
            nonlocal image_prefix
            container = project.container

            build_dir = local.path(project.builddir)
            if __unionfs_is_active(root=build_dir):
                LOG.debug("UnionFS already active in %s", build_dir)
                return func(project, *args, **kwargs)

            image_prefix = local.path(image_prefix)
            abs_base_dir = local.path(container.local)
            abs_image_dir = build_dir / image_dir
            abs_mount_dir = build_dir / mountpoint

            LOG.debug("ABS_IMAGE_DIR: %s", abs_image_dir)
            if image_prefix:
                rel_prj_builddir = os.path.relpath(
                    project.builddir, str(settings.CFG["build_dir"]))
                abs_image_dir = image_prefix / rel_prj_builddir / image_dir

                if is_outside_of_builddir(project, abs_image_dir):
                    update_cleanup_paths(abs_image_dir)
            LOG.debug("ABS_IMAGE_DIR: %s", abs_image_dir)

            if not abs_base_dir.exists():
                abs_base_dir.mkdir()
            if not abs_image_dir.exists():
                abs_image_dir.mkdir()
            if not abs_mount_dir.exists():
                abs_mount_dir.mkdir()

            unionfs_cmd = __unionfs_set_up(abs_base_dir, abs_image_dir,
                                           abs_mount_dir)
            project_builddir_bak = project.builddir
            project.builddir = abs_mount_dir

            proc = unionfs_cmd.popen()
            while (not __unionfs_is_active(root=abs_mount_dir)) and \
                  (proc.poll() is None):
                pass

            ret = None
            if proc.poll() is None:
                try:
                    with local.cwd(abs_mount_dir):
                        ret = func(project, *args, **kwargs)
                finally:
                    project.builddir = project_builddir_bak

                    from signal import SIGINT
                    is_running = proc.poll() is None
                    while __unionfs_is_active(
                            root=abs_mount_dir) and is_running:
                        try:
                            proc.send_signal(SIGINT)
                            proc.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                            is_running = False
                    LOG.debug("Unionfs shut down.")

            if __unionfs_is_active(root=abs_mount_dir):
                raise UnmountError()

            return ret

        return wrap_in_union_fs_func

    return wrap_in_union_fs


def __unionfs_is_active(root):
    real_root = os.path.realpath(root)
    for part in psutil.disk_partitions(all=True):
        if os.path.commonpath([part.mountpoint, real_root]) == real_root:
            if part.fstype in ["fuse.unionfs", "fuse.unionfs-fuse"]:
                return True
    return False


def __unionfs_set_up(ro_base, rw_image, mountpoint):
    """
    Setup a unionfs via unionfs-fuse.

    Args:
        ro_base: base_directory of the project
        rw_image: virtual image of actual file system
        mountpoint: location where ro_base and rw_image merge
    """

    if not mountpoint.exists():
        mountpoint.mkdir()
    if not ro_base.exists():
        LOG.error("Base dir does not exist: '%s'", ro_base)
        raise ValueError("Base directory does not exist")
    if not rw_image.exists():
        LOG.error("Image dir does not exist: '%s'", rw_image)
        raise ValueError("Image directory does not exist")

    from benchbuild.utils.cmd import unionfs as unionfs_cmd
    LOG.debug("Mounting UnionFS on %s with RO:%s RW:%s", mountpoint, ro_base,
              rw_image)
    return unionfs_cmd["-f", "-o", "auto_unmount,allow_other,cow", rw_image +
                       "=RW:" + ro_base + "=RO", mountpoint]


class UnmountError(BaseException):
    pass
