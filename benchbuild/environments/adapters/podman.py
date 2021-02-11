import logging
import os
import typing as tp

from plumbum import local
from plumbum.commands.base import BaseCommand

from benchbuild.settings import CFG
from benchbuild.utils.cmd import podman, rm

LOG = logging.getLogger(__name__)


def bb_podman(*args: str) -> BaseCommand:
    opts = [
        '--root',
        str(CFG['container']['root']), '--runroot',
        str(CFG['container']['runroot'])
    ]
    cmd = podman[opts]
    return cmd[args]


def create_container(
    image_id: str,
    container_name: str,
    mounts: tp.Optional[tp.List[str]] = None
) -> str:
    """
    Create, but do not start, an OCI container.

    Refer to 'buildah create --help' for details about mount
    specifications and '--replace'.

    Args:
        image_id: The container image used as template.
        container_name: The name the container will be given.
        mounts: A list of mount specifications for the OCI runtime.
    """
    podman_create = bb_podman('create', '--replace')

    if mounts:
        for mount in mounts:
            create_cmd = podman_create['--mount', mount]

    cfg_mounts = list(CFG['container']['mounts'].value)
    if cfg_mounts:
        for source, target in cfg_mounts:
            create_cmd = create_cmd['--mount',
                                    f'type=bind,src={source},target={target}']

    container_id = str(create_cmd('--name', container_name, image_id)).strip()

    LOG.debug('created container: %s', container_id)
    return container_id


def save(image_id: str, out_path: str) -> None:
    if local.path(out_path).exists():
        rm(out_path)
    bb_podman('save')('-o', out_path, image_id)


def load(image_name: str, load_path: str) -> None:
    bb_podman('load')('-i', load_path, image_name)


def run_container(name: str) -> None:
    LOG.debug('running container: %s', name)
    container_start = bb_podman('container', 'start')
    container_start['-ai', name].run_tee()


def remove_container(container_id: str) -> None:
    podman_rm = bb_podman('rm')
    podman_rm(container_id)
