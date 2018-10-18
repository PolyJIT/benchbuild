import enum
import logging

from plumbum.commands import ProcessExecutionError
from plumbum import local

from benchbuild.settings import CFG
from benchbuild.utils.path import list_to_path, mkdir_uchroot
from benchbuild.utils.run import run, with_env_recursive

LOG = logging.getLogger(__name__)


def uchroot(*args, **kwargs):
    """
    Return a customizable uchroot command.

    Args:
        args: List of additional arguments for uchroot (typical: mounts)
    Return:
        chroot_cmd
    """
    uchroot_cmd = uchroot_with_mounts(
        *args, uchroot_cmd_fn=uchroot_no_llvm, **kwargs)
    return uchroot_cmd["--"]


def __uchroot_default_opts(uid=0, gid=0):
    return [
        "-C", "-w", "/", "-r", local.cwd, "-u",
        str(uid), "-g",
        str(gid), "-E", "-A"
    ]


def uchroot_no_llvm(*args, uid=0, gid=0, **kwargs):
    """
    Return a customizable uchroot command.

    The command will be executed inside a uchroot environment.

    Args:
        args: List of additional arguments for uchroot (typical: mounts)
    Return:
        chroot_cmd
    """
    uchroot_cmd = uchroot_no_args()
    uchroot_cmd = uchroot_cmd[__uchroot_default_opts(uid, gid)]
    return uchroot_cmd[args]


def uchroot_no_args():
    """Return the uchroot command without any customizations."""
    from benchbuild.utils.cmd import uchroot as uchrt

    prefixes = CFG["container"]["prefixes"].value()
    p_paths, p_libs = uchroot_env(prefixes)
    uchrt = with_env_recursive(
        uchrt,
        LD_LIBRARY_PATH=list_to_path(p_libs),
        PATH=list_to_path(p_paths))

    return uchrt


def uchroot_with_mounts(*args, uchroot_cmd_fn=uchroot_no_args, **kwargs):
    """Return a uchroot command with all mounts enabled."""
    mounts = CFG["container"]["mounts"].value()
    prefixes = CFG["container"]["prefixes"].value()

    uchroot_opts, mounts = _uchroot_mounts("mnt", mounts)
    uchroot_cmd = uchroot_cmd_fn(*uchroot_opts, *args, **kwargs)
    paths, libs = uchroot_env(mounts)
    prefix_paths, prefix_libs = uchroot_env(prefixes)

    uchroot_cmd = with_env_recursive(
        uchroot_cmd,
        LD_LIBRARY_PATH=list_to_path(libs + prefix_libs),
        PATH=list_to_path(paths + prefix_paths))
    return uchroot_cmd


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
            retry(
                pb_cmd,
                retries=retries + 1,
                max_retries=max_retries,
                retcode=retcode,
                retry_retcodes=retry_retcodes)
        else:
            raise


def uretry(cmd, retcode=0):
    retry(
        cmd,
        retcode=retcode,
        retry_retcodes=[
            UchrootEC.MNT_PROC_FAILED.value, UchrootEC.MNT_DEV_FAILED.value,
            UchrootEC.MNT_SYS_FAILED.value, UchrootEC.MNT_PTS_FAILED.value
        ])


def uchroot_clean_env(uchroot_cmd, varnames):
    """Returns a uchroot cmd that runs inside a filtered environment."""
    env = uchroot_cmd["/usr/bin/env"]
    clean_env = env["-u", ",".join(varnames)]
    return clean_env


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


def _uchroot_mounts(prefix, mounts):
    i = 0
    mntpoints = []
    uchroot_opts = []
    for mount in mounts:
        if isinstance(mount, dict):
            src_mount = mount["src"]
            tgt_mount = mount["tgt"]
        else:
            src_mount = mount
            tgt_mount = "{0}/{1}".format(prefix, str(i))
            i = i + 1
        mkdir_uchroot(tgt_mount)
        uchroot_opts.extend(["-M", "{0}:{1}".format(src_mount, tgt_mount)])
        mntpoints.append(tgt_mount)
    return uchroot_opts, mntpoints


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

    root = local.path("/")

    ld_libs = [root / m / "lib" for m in f_mounts]
    ld_libs.extend([root / m / "lib64" for m in f_mounts])

    paths = [root / m / "bin" for m in f_mounts]
    paths.extend([root / m / "sbin" for m in f_mounts])
    paths.extend([root / m for m in f_mounts])
    return paths, ld_libs
