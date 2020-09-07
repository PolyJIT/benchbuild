import abc
import typing as tp

from benchbuild.environments.adapters import buildah, repository
from benchbuild.environments.domain import events, model

from . import messagebus


class AbstractUnitOfWork(abc.ABC):
    registry: repository.AbstractRegistry

    def __enter__(self) -> 'AbstractUnitOfWork':
        return self

    def __exit__(self, *args) -> None:
        self.rollback()

    def collect_new_events(self) -> tp.Generator[events.Event, None, None]:
        for image in self.registry.images:
            while image.events:
                yield image.events.pop(0)

    @abc.abstractmethod
    def create(self, tag: str, layers: tp.List[model.Layer]) -> events.Event:
        raise NotImplementedError

    @abc.abstractmethod
    def add_layer(self, container: model.Container, layer: model.Layer) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError


class BuildahUnitOfWork(AbstractUnitOfWork):

    def __init__(self):
        self.registry = repository.BuildahRegistry()

    def create(self, tag: str, layers: tp.List[model.Layer]) -> events.Event:
        image = self.registry.create(tag, layers)
        event = events.ImageCreated(tag, len(layers))
        messagebus.handle(event, self)
        return image

    def add_layer(self, container: model.Container, layer: model.Layer) -> None:
        buildah.spawn_layer(container, layer)
        messagebus.handle(events.LayerCreated(container.name, str(layer)), self)

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
