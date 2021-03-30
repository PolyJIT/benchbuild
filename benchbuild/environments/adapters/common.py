import typing as tp
from functools import partial

from plumbum import ProcessExecutionError
from plumbum.commands.base import BaseCommand

from benchbuild.settings import CFG
from benchbuild.utils.cmd import podman, buildah


def container_cmd(base: BaseCommand, *args: str) -> BaseCommand:
    opts = [
        '--root',
        str(CFG['container']['root']), '--runroot',
        str(CFG['container']['runroot'])
    ]
    cmd = base[opts]
    return cmd[args]


bb_podman: tp.Callable[[...], BaseCommand] = partial(container_cmd, podman)
bb_buildah: tp.Callable[[...], BaseCommand] = partial(container_cmd, buildah)

MaybeCommandError = tp.Optional[ProcessExecutionError]


def run(cmd: BaseCommand, **kwargs: tp.Any) -> tp.Tuple[str, MaybeCommandError]:
    result = ""
    try:
        result = str(cmd(**kwargs)).strip()
    except ProcessExecutionError as err:
        return result, err

    return result, None


def run_tee(cmd: BaseCommand,
            **kwargs: tp.Any) -> tp.Tuple[str, MaybeCommandError]:
    result = ""
    try:
        result = cmd.run_tee(**kwargs)
    except ProcessExecutionError as err:
        return result, err
    return result, None
