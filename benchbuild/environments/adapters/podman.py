import os

from plumbum.commands.base import BaseCommand

from benchbuild.settings import CFG
from benchbuild.utils.cmd import podman

PODMAN_DEFAULT_OPTS = [
    '--root',
    os.path.abspath(str(CFG['container']['root'])), '--runroot',
    os.path.abspath(str(CFG['container']['runroot']))
]


def bb_podman() -> BaseCommand:
    return podman[PODMAN_DEFAULT_OPTS]


BB_PODMAN_RUN: BaseCommand = bb_podman()['run']
BB_PODMAN_CREATE: BaseCommand = bb_podman()['create']


def create_container(image_id: str, container_name: str) -> str:
    container_id = str(BB_PODMAN_CREATE('--name', container_name,
                                        image_id)).strip()
    return container_id


def run_container(name: str) -> None:
    BB_PODMAN_RUN('-it', name)
