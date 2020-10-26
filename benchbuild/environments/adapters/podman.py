import logging
import os
import typing as tp

from plumbum.commands.base import BaseCommand

from benchbuild.settings import CFG
from benchbuild.utils.cmd import podman

LOG = logging.getLogger(__name__)
PODMAN_DEFAULT_OPTS = [
    '--root',
    os.path.abspath(str(CFG['container']['root'])), '--runroot',
    os.path.abspath(str(CFG['container']['runroot']))
]


def bb_podman() -> BaseCommand:
    return podman[PODMAN_DEFAULT_OPTS]


BB_PODMAN_CONTAINER_START: BaseCommand = bb_podman()['container', 'start']
BB_PODMAN_CREATE: BaseCommand = bb_podman()['create']
BB_PODMAN_RM: BaseCommand = bb_podman()['rm']


def create_container(
    image_id: str,
    container_name: str,
    mounts: tp.Optional[tp.List[str]] = None
) -> str:
    create_cmd = BB_PODMAN_CREATE['--replace']

    if mounts:
        for mount in mounts:
            create_cmd = create_cmd['--mount', mount]

    cfg_mounts = list(CFG['container']['mounts'].value)
    if cfg_mounts:
        for source, target in cfg_mounts:
            create_cmd = create_cmd['--mount', f'{source}:{target}']

    container_id = str(
        create_cmd('--name', container_name.lower(), image_id.lower())
    ).strip()

    LOG.debug('created container: %s', container_id)
    return container_id


def run_container(name: str) -> None:
    LOG.debug('running container: %s', name)
    BB_PODMAN_CONTAINER_START['-ai', name].run_tee()


def remove_container(container_id: str) -> None:
    BB_PODMAN_RM(container_id)
