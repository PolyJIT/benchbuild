import abc
import typing as tp

from benchbuild.environments.adapters import buildah, podman, repository
from benchbuild.environments.domain import events, model

from . import messagebus


class AbstractUnitOfWork(abc.ABC):
    registry: repository.AbstractRegistry

    def collect_new_events(self) -> tp.Generator[events.Event, None, None]:
        for image in self.registry.images:
            while image.events:
                yield image.events.pop(0)

    def __enter__(self) -> 'AbstractUnitOfWork':
        return self

    def __exit__(self, *args: tp.Any) -> None:
        self.rollback()

    @abc.abstractmethod
    def _create(
        self, tag: str, layers: tp.List[model.Layer]
    ) -> model.Container:
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError


class AbstractImageUnitOfWork(AbstractUnitOfWork):

    def add_layer(self, container: model.Container, layer: model.Layer) -> None:
        messagebus.handle(
            events.CreatingLayer(container.name, str(layer)), self
        )
        self._add_layer(container, layer)
        messagebus.handle(events.LayerCreated(container.name, str(layer)), self)

    def create(self, tag: str, layers: tp.List[model.Layer]) -> model.Container:
        container = self._create(tag, layers)
        event = events.ImageCreated(
            tag, str(container.image.from_), len(layers)
        )
        messagebus.handle(event, self)
        return container

    @abc.abstractmethod
    def _add_layer(
        self, container: model.Container, layer: model.Layer
    ) -> None:
        raise NotImplementedError


class BuildahUnitOfWork(AbstractUnitOfWork):

    def __init__(self) -> None:
        self.registry = repository.BuildahRegistry()

    def _create(
        self, tag: str, layers: tp.List[model.Layer]
    ) -> model.Container:
        return self.registry.create(tag, layers)

    def _add_layer(
        self, container: model.Container, layer: model.Layer
    ) -> None:
        buildah.spawn_layer(container, layer)

    def rollback(self) -> None:
        for container in self.registry.containers:
            buildah.destroy_working_container(container)
            buildah.destroy_build_context(container.context)
            messagebus.handle(events.ImageDestroyed(container.name), self)

    def commit(self) -> None:
        for container in self.registry.containers:
            buildah.commit_working_container(container)
            buildah.destroy_build_context(container.context)
            messagebus.handle(events.ImageCommitted(container.name), self)


class AbstractContainerUOW(AbstractUnitOfWork):
    registry: repository.AbstractRegistry

    def create(self, image_id: str, container_name: str) -> model.Container:
        container = self._create(image_id, container_name)
        event = events.ContainerCreated(image_id, container_name)
        messagebus.handle(event, self)
        return container


class PodmanUnitOfWork(AbstractContainerUOW):

    def __init__(self) -> None:
        self.registry = repository.BuildahRegistry()

    def _create(self, image_id: str, container_name: str) -> model.Container:
        image = self.registry.get(image_id)
        if image:
            container_id = podman.create_container(image.name, container_name)
            return model.Container(container_id, image, '')
        raise ValueError('Image not found. Try building it first.')

    def run_container(self, container: model.Container) -> None:
        podman.run_container(container.name)

    def rollback(self) -> None:
        # Remove container.
        pass

    def commit(self) -> None:
        # Commit completed container as a result image, if the user wants it.
        pass
