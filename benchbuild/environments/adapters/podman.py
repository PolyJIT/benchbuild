import logging
import os

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


def create_container(image_id: str, container_name: str) -> str:
    container_id = str(
        BB_PODMAN_CREATE('--replace', '--name', container_name, image_id)
    ).strip()

    LOG.debug('created container: %s', container_id)
    return container_id


def run_container(name: str) -> None:
    LOG.debug('running container: %s', name)
    BB_PODMAN_CONTAINER_START['-ai', name].run_tee()


def remove_container(container_id: str) -> None:
    BB_PODMAN_RM(container_id)
