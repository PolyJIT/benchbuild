import logging
import typing as tp

from plumbum import ProcessExecutionError
from plumbum.commands.base import BaseCommand
from result import Ok, Err, Result

from benchbuild.settings import CFG
from benchbuild.utils.cmd import podman, buildah

LOG = logging.getLogger(__name__)

__MSG_SHORTER_PATH_REQUIRED = (
    'needs to be shorter than 50 chars, if you '
    'experience errors with the following command.'
)


def buildah_version() -> tp.Tuple[int, int, int]:
    """
    Returns the local buildah version.
    """
    raw_version_string = buildah("version")
    version_str = raw_version_string.split('\n')[0].split(":")[1].strip()
    major, minor, patch = version_str.split('.')
    return (int(major), int(minor), int(patch))


def container_cmd(base: BaseCommand) -> BaseCommand:
    """
    Capture a plumbum command and apply common options.

    This adds options for container root and runroot storage locations
    to the plumbum command. Useful for podman/buildah commands.

    Args:
        base: A plumbum base command.

    Returns:
        A plumbum base command augmented by root/runroot parameters.
    """

    def path_longer_than_50_chars(path: str) -> bool:
        if len(path) > 50:
            LOG.debug('A path-length > 50 is not supported by libpod.')
            return True
        return False

    def wrapped_cmd(*args: str) -> BaseCommand:
        root = CFG['container']['root']
        runroot = CFG['container']['runroot']
        storage_driver = CFG['container']['storage_driver'].value
        storage_opts = CFG['container']['storage_opts'].value

        if path_longer_than_50_chars(str(root)):
            LOG.error(
                '%s - %s', root.__to_env_var__(), __MSG_SHORTER_PATH_REQUIRED
            )

        if path_longer_than_50_chars(str(runroot)):
            LOG.error(
                '%s - %s', runroot.__to_env_var__(), __MSG_SHORTER_PATH_REQUIRED
            )

        opts = ['--root', root, '--runroot', runroot]

        if storage_driver:
            opts.append('--storage-driver')
            opts.append(storage_driver)

        if storage_opts is None:
            # ignore options set in 'storage.conf'
            opts.append("--storage-opt=''")

        for opt in storage_opts:
            opts.append('--storage-opt')
            opts.append(opt)

        cmd = base[opts]
        return cmd[args]

    return wrapped_cmd


bb_podman = container_cmd(podman)
bb_buildah = container_cmd(buildah)


class ImageCreateError(Exception):

    def __init__(self, name: str, message: str):
        super().__init__()

        self.name = name
        self.message = message


def run(cmd: BaseCommand,
        **kwargs: tp.Any) -> Result[str, ProcessExecutionError]:
    try:
        return Ok(str(cmd(**kwargs)).strip())
    except ProcessExecutionError as err:
        return Err(err)


def run_tee(cmd: BaseCommand,
            **kwargs: tp.Any) -> Result[tp.Any, ProcessExecutionError]:
    try:
        return Ok(cmd.run_tee(**kwargs))
    except ProcessExecutionError as err:
        return Err(err)


def run_fg(cmd: BaseCommand,
           **kwargs: tp.Any) -> Result[tp.Any, ProcessExecutionError]:
    try:
        return Ok(cmd.run_fg(**kwargs))
    except ProcessExecutionError as err:
        return Err(err)
