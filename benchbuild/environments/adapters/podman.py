import abc
import logging
import typing as tp

from plumbum import local
from rich import print
from rich.markdown import Markdown

from benchbuild.environments.adapters import buildah
from benchbuild.environments.adapters.common import (
    run,
    run_tee,
    run_fg,
    bb_podman,
    MaybeCommandError,
)
from benchbuild.environments.domain import model, events
from benchbuild.settings import CFG
from benchbuild.utils.cmd import rm

LOG = logging.getLogger(__name__)


class ContainerCreateError(Exception):

    def __init__(self, name: str, message: str):
        super().__init__()

        self.name = name
        self.message = message


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

    create_cmd = podman_create
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


def save(image_id: str, out_path: str) -> MaybeCommandError:
    if local.path(out_path).exists():
        LOG.warning("No image exported. Image exists.")
        return None
    _, err = run(bb_podman('save')['-o', out_path, image_id])
    return err


def load(load_path: str) -> MaybeCommandError:
    _, err = run(bb_podman('load')['-i', load_path])
    return err


def run_container(name: str) -> MaybeCommandError:
    container_start = bb_podman('container', 'start')
    _, err = run_tee(container_start['-ai', name])
    return err


def remove_container(container_id: str) -> MaybeCommandError:
    podman_rm = bb_podman('rm')
    _, err = run(podman_rm[container_id])
    return err


class ContainerRegistry(abc.ABC):
    containers: tp.Dict[str, model.Container]
    ro_images: buildah.BuildahImageRegistry

    def __init__(self) -> None:
        self.containers = dict()
        self.ro_images = buildah.BuildahImageRegistry()

    def find(self, container_id: str) -> model.MaybeContainer:
        if container_id in self.containers:
            return self.containers[container_id]

        container = self._find(container_id)
        if container is not None:
            self.containers[container_id] = container
            return container

        return None

    def find_image(self, tag: str) -> model.MaybeImage:
        return self.ro_images.find(tag)

    def env(self, tag: str, env_name: str) -> tp.Optional[str]:
        return self.ro_images.env(tag, env_name)

    def mount(self, tag: str, src: str, tgt: str) -> None:
        self.ro_images.temporary_mount(tag, src, tgt)

    @abc.abstractmethod
    def _find(self, tag: str) -> model.MaybeContainer:
        raise NotImplementedError

    def create(self, image_id: str, name: str) -> model.Container:
        image = self.find_image(image_id)
        assert image

        container = self._create(image, name)
        if container is not None:
            self.containers[name] = container
        return container

    @abc.abstractmethod
    def _create(self, image: model.Image, name: str) -> model.Container:
        raise NotImplementedError

    def start(self, container: model.Container) -> None:
        if container.name not in self.containers:
            raise ValueError('container must be created first')

        self._start(container)

    @abc.abstractmethod
    def _start(self, container: model.Container) -> None:
        raise NotImplementedError


_DEBUG_CONTAINER_SESSION_INTRO = """
# Debug Session
Your are running in an interactive session of **{container_name}**.

The container's entrypoint has been replaced with a default shell.
The original entrypoint would be:

    {entrypoint}

You can exit this mode by leaving the shell using `exit`. If your last
command did not return an exit code of ``0``, benchbuild will report an
error.
"""


class PodmanRegistry(ContainerRegistry):

    def _create(self, image: model.Image, name: str) -> model.Container:
        mounts = [
            f'type=bind,src={mnt.source},target={mnt.target}'
            for mnt in image.mounts
        ]
        interactive = bool(CFG['container']['interactive'])

        create_cmd = bb_podman('create', '--replace')
        if interactive:
            create_cmd = create_cmd['-it', '--entrypoint', '/bin/sh']

        if mounts:
            for mount in mounts:
                create_cmd = create_cmd['--mount', mount]

        cfg_mounts = list(CFG['container']['mounts'].value)
        if cfg_mounts:
            for source, target in cfg_mounts:
                create_cmd = create_cmd[
                    '--mount', f'type=bind,src={source},target={target}']

        container_id, err = run(create_cmd['--name', name, image.name])
        if err:
            raise ContainerCreateError(
                container_id, " ".join(err.argv)
            ) from err

        # If we had to replace an existing container (bug?), we get 2 IDs.
        # The first ID is the old (replaced) container.
        # The second ID is the new container.
        new_container_id = container_id.split('\n')[-1]

        return model.Container(new_container_id, image, '', name)

    def _start(self, container: model.Container) -> None:
        container_id = container.container_id
        container_start = bb_podman('container', 'start')
        interactive = bool(CFG['container']['interactive'])

        if interactive:
            entrypoint = buildah.find_entrypoint(container.image.name)
            print(
                Markdown(
                    _DEBUG_CONTAINER_SESSION_INTRO.format(
                        container_name=container.name,
                        entrypoint=entrypoint,
                    )
                )
            )

            _, err = run_fg(container_start['-ai', container_id])
        else:
            _, err = run_tee(container_start['-ai', container_id])

        if err:
            container.events.append(
                events.ContainerStartFailed(
                    container.name, container_id, " ".join(err.argv)
                )
            )
        else:
            container.events.append(events.ContainerStarted(container_id))

    def _find(self, tag: str) -> model.MaybeContainer:
        return None
