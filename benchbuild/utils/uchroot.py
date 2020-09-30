import enum
import logging
import os
import typing as tp

from plumbum import local
from plumbum.commands import ProcessExecutionError
from plumbum.commands.base import BoundCommand

from benchbuild.settings import CFG
from benchbuild.utils import path, run

LOG = logging.getLogger(__name__)


def uchroot(*args, **kwargs):
    """
    Return a customizable uchroot command.

    Args:
        args: List of additional arguments for uchroot (typical: mounts)
    Return:
        chroot_cmd
    """
    uchroot_cmd = with_mounts(*args, uchroot_cmd_fn=no_llvm, **kwargs)
    return uchroot_cmd["--"]


def __default_opts__(uid=0, gid=0):
    return [
        "-C", "-w", "/", "-r", local.cwd, "-u",
        str(uid), "-g",
        str(gid), "-E", "-A"
    ]


def no_llvm(*args, uid=0, gid=0, **kwargs):
    """
    Return a customizable uchroot command.

    The command will be executed inside a uchroot environment.

    Args:
        args: List of additional arguments for uchroot (typical: mounts)
    Return:
        chroot_cmd
    """
    del kwargs
    uchroot_cmd = no_args()
    uchroot_cmd = uchroot_cmd[__default_opts__(uid, gid)]
    return uchroot_cmd[args]


def no_args(**kwargs):
    """Return the uchroot command without any customizations."""
    del kwargs

    from benchbuild.utils.cmd import uchroot as uchrt

    prefixes = CFG["container"]["prefixes"].value
    p_paths, p_libs = env(prefixes)
    uchrt = run.with_env_recursive(
        uchrt,
        LD_LIBRARY_PATH=path.list_to_path(p_libs),
        PATH=path.list_to_path(p_paths)
    )

    return uchrt


def with_mounts(*args, uchroot_cmd_fn=no_args, **kwargs):
    """Return a uchroot command with all mounts enabled."""
    _mounts = CFG["container"]["mounts"].value
    prefixes = CFG["container"]["prefixes"].value

    uchroot_opts, _mounts = __mounts__("mnt", _mounts)
    uchroot_cmd = uchroot_cmd_fn(**kwargs)
    uchroot_cmd = uchroot_cmd[uchroot_opts]
    uchroot_cmd = uchroot_cmd[args]
    paths, libs = env(_mounts)
    prefix_paths, prefix_libs = env(prefixes)

    uchroot_cmd = run.with_env_recursive(
        uchroot_cmd,
        LD_LIBRARY_PATH=path.list_to_path(libs + prefix_libs),
        PATH=path.list_to_path(paths + prefix_paths)
    )
    return uchroot_cmd


class UchrootEC(enum.Enum):
    MNT_FAILED = 255
    MNT_PROC_FAILED = 254
    MNT_DEV_FAILED = 253
    MNT_SYS_FAILED = 252
    MNT_PTS_FAILED = 251


def retry(
    pb_cmd: BoundCommand,
    retries: int = 0,
    max_retries: int = 10,
    retcode: int = 0,
    retry_retcodes: tp.Optional[tp.List[int]] = None
) -> None:
    try:
        pb_cmd.run_fg(retcode=retcode)
    except ProcessExecutionError as proc_ex:
        new_retcode = proc_ex.retcode
        if retries > max_retries:
            LOG.error("Retried %d times. No change. Abort", retries)
            raise

        if retry_retcodes and new_retcode in retry_retcodes:
            retry(
                pb_cmd,
                retries=retries + 1,
                max_retries=max_retries,
                retcode=retcode,
                retry_retcodes=retry_retcodes
            )
        else:
            raise


def uretry(cmd: BoundCommand, retcode: int = 0) -> None:
    retry(
        cmd,
        retcode=retcode,
        retry_retcodes=[
            UchrootEC.MNT_PROC_FAILED.value, UchrootEC.MNT_DEV_FAILED.value,
            UchrootEC.MNT_SYS_FAILED.value, UchrootEC.MNT_PTS_FAILED.value
        ]
    )


def clean_env(
    uchroot_cmd: BoundCommand, varnames: tp.List[str]
) -> BoundCommand:
    """Returns a uchroot cmd that runs inside a filtered environment."""
    _env = uchroot_cmd["/usr/bin/env"]
    __clean_env = _env["-u", ",".join(varnames)]
    return __clean_env


def mounts(prefix: str, __mounts: tp.List) -> tp.List[str]:
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
    for mount in __mounts:
        if not isinstance(mount, dict):
            mntpoint = "{0}/{1}".format(prefix, str(i))
            mntpoints.append(mntpoint)
            i = i + 1
    return mntpoints


def __mounts__(prefix: str,
               _mounts: tp.List) -> tp.Tuple[tp.List[str], tp.List[str]]:
    i = 0
    mntpoints = []
    uchroot_opts = []
    for mount in _mounts:
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


def env(
    uchroot_mounts: tp.List[str]
) -> tp.Tuple[tp.List[local.path], tp.List[local.path]]:
    """
    Compute the environment of the change root for the user.

    Args:
        uchroot_mounts: The mountpoints of the current user.
    Return:
        paths
        ld_libs
    """
    f_mounts = [m.strip("/") for m in uchroot_mounts]

    root = local.path("/")

    ld_libs = [root / m / "lib" for m in f_mounts]
    ld_libs.extend([root / m / "lib64" for m in f_mounts])

    paths = [root / m / "bin" for m in f_mounts]
    paths.extend([root / m / "sbin" for m in f_mounts])
    paths.extend([root / m for m in f_mounts])
    return paths, ld_libs


def mkdir_uchroot(dirpath: str, root: str = ".") -> None:
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
    _uchroot = no_args()
    _uchroot = _uchroot["-E", "-A", "-C", "-w", "/", "-r"]
    _uchroot = _uchroot[os.path.abspath(root)]
    uretry(_uchroot["--", "/bin/mkdir", "-p", dirpath])


def mkfile_uchroot(filepath: str, root: str = ".") -> None:
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
    _uchroot = no_args()
    _uchroot = _uchroot["-E", "-A", "-C", "-w", "/", "-r"]
    _uchroot = _uchroot[os.path.abspath(root)]
    uretry(_uchroot["--", "/bin/touch", filepath])
