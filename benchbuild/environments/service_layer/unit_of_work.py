import abc
import typing as tp

from benchbuild.environments.adapters import buildah, podman, repository
from benchbuild.environments.domain import events, model


class AbstractUnitOfWork(abc.ABC):
    registry: repository.AbstractRegistry

    def collect_new_events(self) -> tp.Generator[events.Event, None, None]:
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


class ContainerImagesUOW(AbstractUnitOfWork):

    def __init__(self) -> None:
        self.registry = repository.BuildahRegistry()

    def _create_image(
        self, tag: str, layers: tp.List[model.Layer]
    ) -> model.Container:
        return self.registry.create_image(tag, layers)

    def _create_container(
        self, image_id: str, container_name: str
    ) -> model.Container:
        image = self.registry.get_image(image_id)
        if image:
            return self.registry.create_container(image, container_name)
        raise ValueError('Image not found. Try building it first.')

    def _add_layer(
        self, container: model.Container, layer: model.Layer
    ) -> None:
        buildah.spawn_layer(container, layer)

    def rollback(self) -> None:
        while self.registry.build_containers:
            container = self.registry.build_containers.pop()
            buildah.destroy_working_container(container)
            buildah.destroy_build_context(container.context)

        while self.registry.containers:
            container = self.registry.containers.pop()
            podman.remove_container(container.container_id)

    def commit(self) -> None:
        while self.registry.build_containers:
            container = self.registry.build_containers.pop()
            buildah.commit_working_container(container)
            buildah.destroy_build_context(container.context)

        #for container in self.registry.containers:
        #    podman.commit(container)
        #    podman.destroy(container)
