import abc
import logging
import sys
import typing as tp
from typing import Protocol

from plumbum import local
from plumbum.path.utils import delete
from result import Err

from benchbuild.environments.adapters import common, buildah, podman
from benchbuild.environments.domain import model, events

LOG = logging.getLogger(__name__)


class EventCollector(Protocol):

    def collect_new_events(self) -> tp.Generator[model.Message, None, None]:
        ...


class UnitOfWork(abc.ABC):

    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError


class ImageUnitOfWork(UnitOfWork):
    registry: buildah.ImageRegistry
    events: tp.List[model.Message] = []

    def collect_new_events(self) -> tp.Generator[model.Message, None, None]:
        for image in self.registry.images.values():
            while image.events:
                evt = image.events.pop(0)
                yield evt

        while self.events:
            evt = self.events.pop(0)
            yield evt

    def __enter__(self) -> 'ImageUnitOfWork':
        return self

    def __exit__(self, *args: tp.Any) -> None:
        self.rollback()

    def create(self, tag: str, from_: str) -> model.MaybeContainer:
        try:
            return self._create(tag, from_)
        except common.ImageCreateError as ex:
            self.events.append(events.ImageCreationFailed(tag, ex.message))
        return None

    @abc.abstractmethod
    def _create(self, tag: str, from_: str) -> model.MaybeContainer:
        raise NotImplementedError

    def destroy(self, image: model.Image) -> None:
        self._destroy(image.name)

    @abc.abstractmethod
    def _destroy(self, tag: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _export_image(self, image_id: str, out_path: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _import_image(self, import_path: str) -> None:
        raise NotImplementedError

    def export_image(self, image_id: str, out_path: str) -> None:
        return self._export_image(image_id, out_path)

    def import_image(self, import_path: str) -> None:
        return self._import_image(import_path)

    def rollback(self) -> None:
        containers = self.registry.containers
        for container in containers.values():
            self._rollback(container)

    @abc.abstractmethod
    def _rollback(self, container: model.Container) -> None:
        raise NotImplementedError

    def commit(self) -> None:
        containers = self.registry.containers
        for container in containers.values():
            self._commit(container)

    @abc.abstractmethod
    def _commit(self, container: model.Container) -> None:
        raise NotImplementedError


class BuildahImageUOW(ImageUnitOfWork):

    def __init__(self) -> None:
        self.registry = buildah.BuildahImageRegistry()

    def _create(self, tag: str, from_: str) -> model.MaybeContainer:
        from_layer = model.FromLayer(from_)
        return self.registry.create(tag, from_layer)

    def _destroy(self, tag: str) -> None:
        common.run(common.bb_buildah('rmi')['-f', tag])

    def _export_image(self, image_id: str, out_path: str) -> None:
        podman.save(image_id, out_path)

    def _import_image(self, import_path: str) -> None:
        podman.load(import_path)

    def _commit(self, container: model.Container) -> None:
        image = container.image
        res = common.run(
            common.bb_buildah('commit')[container.container_id,
                                        image.name.lower()]
        )

        if isinstance(res, Err):
            LOG.error("Could not commit container image %s", image.name)
            LOG.error("Reason: %s", str(res.unwrap_err))

    def _rollback(self, container: model.Container) -> None:
        buildah.run(buildah.bb_buildah('rm')[container.container_id])
        context_path = local.path(container.context)
        if context_path.exists():
            delete(context_path)


class ContainerUnitOfWork(UnitOfWork):
    registry: podman.ContainerRegistry

    def __enter__(self) -> 'ContainerUnitOfWork':
        return self

    def __exit__(self, *args: tp.Any) -> None:
        self.rollback()

    def collect_new_events(self) -> tp.Generator[model.Message, None, None]:
        for container in self.registry.containers.values():
            while container.events:
                yield container.events.pop(0)

    def create(
        self, image_id: str, name: str, args: tp.Sequence[str]
    ) -> model.Container:
        return self._create(image_id, name, args)

    @abc.abstractmethod
    def _create(
        self, tag: str, name: str, args: tp.Sequence[str]
    ) -> model.Container:
        raise NotImplementedError

    def start(self, container: model.Container) -> None:
        self._start(container)

    @abc.abstractmethod
    def _start(self, container: model.Container) -> None:
        raise NotImplementedError

    def rollback(self) -> None:
        pass

    def commit(self) -> None:
        pass


class PodmanContainerUOW(ContainerUnitOfWork):

    def __init__(self) -> None:
        self.registry = podman.PodmanRegistry()

    def _create(
        self, tag: str, name: str, args: tp.Sequence[str]
    ) -> model.Container:
        return self.registry.create(tag, name, args)

    def _start(self, container: model.Container) -> None:
        self.registry.start(container)


class AbstractUnitOfWork(abc.ABC):
    registry: buildah.ImageRegistry

    def collect_new_events(self) -> tp.Generator[model.Message, None, None]:
        for image in self.registry.images.values():
            while image.events:
                yield image.events.pop(0)

    def __enter__(self) -> 'AbstractUnitOfWork':
        return self

    def __exit__(self, *args: tp.Any) -> None:
        self.rollback()

    def add_layer(self, container: model.Container, layer: model.Layer) -> None:
        self._add_layer(container, layer)

    def create_image(
        self, tag: str, layers: tp.List[model.Layer]
    ) -> model.Container:
        return self._create_image(tag, layers)

    def create_container(
        self, image_id: str, container_name: str
    ) -> model.Container:
        return self._create_container(image_id, container_name)

    def export_image(self, image_id: str, out_path: str) -> None:
        return self._export_image(image_id, out_path)

    def import_image(self, import_path: str) -> None:
        return self._import_image(import_path)

    def run_container(self, container: model.Container) -> None:
        podman.run_container(container.container_id)

    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _create_image(
        self, tag: str, layers: tp.List[model.Layer]
    ) -> model.Container:
        raise NotImplementedError

    @abc.abstractmethod
    def _add_layer(
        self, container: model.Container, layer: model.Layer
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _create_container(
        self, image_id: str, container_name: str
    ) -> model.Container:
        raise NotImplementedError

    @abc.abstractmethod
    def _export_image(self, image_id: str, out_path: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _import_image(self, import_path: str) -> None:
        raise NotImplementedError
