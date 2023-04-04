import abc
import logging
import typing as tp

from plumbum import local, ProcessExecutionError
from result import Result, Err, Ok
from rich import print

from benchbuild.environments.adapters import buildah
from benchbuild.environments.adapters.common import (
    run,
    run_tee,
    run_fg,
    bb_podman,
)
from benchbuild.environments.domain import model, events
from benchbuild.settings import CFG

LOG = logging.getLogger(__name__)


class ContainerCreateError(Exception):

    def __init__(self, name: str, message: str):
        super().__init__()

        self.name = name
        self.message = message


def save(image_id: str, out_path: str) -> Result[bool, ProcessExecutionError]:
    if local.path(out_path).exists():
        LOG.warning("No image exported. Image exists.")
        return Ok(True)

    res = run(bb_podman('save')['-o', out_path, image_id])

    if isinstance(res, Err):
        LOG.error("Could not save the image %s to %s.", image_id, out_path)
        LOG.error("Reason: %s", str(res.unwrap_err()))
        return res
    return Ok(True)


def load(load_path: str) -> Result[bool, ProcessExecutionError]:
    res = run(bb_podman('load')['-i', load_path])
    if isinstance(res, Err):
        LOG.error("Could not load the image from %s", load_path)
        LOG.error("Reason: %s", str(res.unwrap_err()))
        return res
    return Ok(True)


def run_container(name: str) -> Result[str, ProcessExecutionError]:
    container_start = bb_podman('container', 'start')
    res = run_tee(container_start['-ai', name])
    if isinstance(res, Err):
        LOG.error("Could not run the container %s", name)
        LOG.error("Reason: %s", str(res.unwrap_err()))

    return res


def remove_container(container_id: str) -> Result[str, ProcessExecutionError]:
    podman_rm = bb_podman('rm')
    res = run(podman_rm[container_id])
    if isinstance(res, Err):
        LOG.error("Could not remove the container %s", container_id)
        LOG.error("Reason: %s", str(res.unwrap_err()))

    return res


class ContainerRegistry(abc.ABC):
    containers: tp.Dict[str, model.Container]
    ro_images: buildah.BuildahImageRegistry

    def __init__(self) -> None:
        self.containers = dict()
        self.ro_images = buildah.BuildahImageRegistry()

    def find(self, container_id: str) -> model.MaybeContainer:
        if container_id in self.containers:
            return self.containers[container_id]

        if (container := self._find(container_id)) is not None:
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

    def create(
        self, image_id: str, name: str, args: tp.Sequence[str]
    ) -> model.Container:
        image = self.find_image(image_id)
        assert image

        container = self._create(image, name, args)
        if container is not None:
            self.containers[name] = container
        return container

    @abc.abstractmethod
    def _create(
        self, image: model.Image, name: str, args: tp.Sequence[str]
    ) -> model.Container:
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
The original entrypoint (with arguments) would be:

    {entrypoint} {arguments}

You can exit this mode by leaving the shell using `exit`. If your last
command did not return an exit code of ``0``, benchbuild will report an
error.
"""


class PodmanRegistry(ContainerRegistry):

    def _create(
        self, image: model.Image, name: str, args: tp.Sequence[str]
    ) -> model.Container:
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

        if (cfg_mounts := list(CFG['container']['mounts'].value)):
            for source, target in cfg_mounts:
                create_cmd = create_cmd[
                    '--mount', f'type=bind,src={source},target={target}']

        if interactive:
            # pylint: disable=import-outside-toplevel
            from rich.markdown import Markdown

            entrypoint = buildah.find_entrypoint(image.name)
            print(
                Markdown(
                    _DEBUG_CONTAINER_SESSION_INTRO.format(
                        container_name=name,
                        entrypoint=entrypoint,
                        arguments=' '.join(args)
                    )
                )
            )

            res = run(create_cmd['--name', name, image.name])
        else:
            res = run(create_cmd['--name', name, image.name][args])

        if isinstance(res, Err):
            LOG.error(
                "Could not create the container %s from %s", name, image.name
            )
            LOG.error("Reason: %s", str(res.unwrap_err()))

            raise ContainerCreateError(name, " ".join(res.unwrap_err().argv))

        # If we had to replace an existing container (bug?), we get 2 IDs.
        # The first ID is the old (replaced) container.
        # The second ID is the new container.
        container_id = res.unwrap()
        new_container_id = container_id.split('\n')[-1]

        return model.Container(new_container_id, image, '', name)

    def _start(self, container: model.Container) -> None:
        container_id = container.container_id
        container_start = bb_podman('container', 'start')
        interactive = bool(CFG['container']['interactive'])

        if interactive:
            res = run_fg(container_start['-ai', container_id])
        else:
            res = run_tee(container_start['-ai', container_id])

        if isinstance(res, Err):
            LOG.error("Could not start the container %s", container_id)
            LOG.error("Reason: %s", str(res.unwrap_err()))

            container.events.append(
                events.ContainerStartFailed(
                    container.name, container_id,
                    " ".join(res.unwrap_err().argv)
                )
            )
        else:
            container.events.append(events.ContainerStarted(container_id))

    def _find(self, tag: str) -> model.MaybeContainer:
        return None
