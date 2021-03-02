import abc
import typing as tp

from benchbuild.environments.adapters import buildah, podman
from benchbuild.environments.domain import commands, events, model


class EventCollector(tp.Protocol):

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

    def collect_new_events(self) -> tp.Generator[model.Message, None, None]:
        for image in self.registry.images.values():
            while image.events:
                evt = image.events.pop(0)
                yield evt

    def __enter__(self) -> 'ImageUnitOfWork':
        return self

    def __exit__(self, *args: tp.Any) -> None:
        self.rollback()

    def create(self, tag: str, from_: str) -> model.Container:
        return self._create(tag, from_)

    @abc.abstractmethod
    def _create(self, tag: str, from_: str) -> model.Container:
        raise NotImplementedError

    def add_layer(self, container: model.Container, layer: model.Layer) -> None:
        image = container.image
        self._add_layer(container, layer)
        image.events.append(events.LayerCreated(image.name, str(layer)))

    @abc.abstractmethod
    def _add_layer(
        self, container: model.Container, layer: model.Layer
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _export_image(self, image_id: str, out_path: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _import_image(self, image_name: str, import_path: str) -> None:
        raise NotImplementedError

    def export_image(self, image_id: str, out_path: str) -> None:
        return self._export_image(image_id, out_path)

    def import_image(self, image_name: str, import_path: str) -> None:
        return self._import_image(image_name, import_path)

    def rollback(self) -> None:
        containers = self.registry.containers
        delete_containers = [
            c for c in containers
            if self.registry.is_held(c) or c.image.is_complete()
        ]

        keep_containers = [
            c for c in containers if not self.registry.is_held(c)
        ]

        for container in delete_containers:
            self.registry.destroy(container)

        for container in keep_containers:
            self.registry.unhold(container)

        self.registry.containers = containers

    def commit(self) -> None:
        containers = self.registry.containers
        for container in containers:
            self.registry.commit(container)
            if not self.registry.is_held(container):
                self.registry.destroy(container)


class BuildahImageUOW(ImageUnitOfWork):

    def __init__(self) -> None:
        self.registry = buildah.BuildahImageRegistry()

    def _create(self, tag: str, from_: str) -> model.Container:
        from_layer = model.FromLayer(from_)
        return self.registry.create(tag, from_layer)

    def _add_layer(
        self, container: model.Container, layer: model.Layer
    ) -> None:
        image = container.image
        image.events.append(
            commands.CreateLayer(image.name, container.container_id, layer)
        )

    def _export_image(self, image_id: str, out_path: str) -> None:
        podman.save(image_id, out_path)

    def _import_image(self, image_name: str, import_path: str) -> None:
        podman.load(image_name, import_path)


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

    def create(self, image_id: str, name: str) -> model.Container:
        return self._create(image_id, name)

    @abc.abstractmethod
    def _create(self, tag: str, container_name: str) -> model.Container:
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

    def _create(self, tag: str, name: str) -> model.Container:
        return self.registry.create(tag, name)

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

    def import_image(self, image_name: str, import_path: str) -> None:
        return self._import_image(image_name, import_path)

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
    def _import_image(self, image_name: str, import_path: str) -> None:
        raise NotImplementedError
