import abc
import typing as tp

import attr

from benchbuild.environments.domain import model
from benchbuild.environments.service_layer import buildah


@attr.s
class AbstractRegistry(abc.ABC):
    seen: tp.Set[model.Image] = attr.ib(default=attr.Factory(set))

    def add(self, image: model.Image) -> None:
        self._add(image)
        self.seen.add(image)

    def get(self, tag: str) -> model.MaybeImage:
        image = self._get(tag)
        if image:
            self.seen.add(image)
        return image

    @abc.abstractmethod
    def _add(self, image: model.Image) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, tag: str) -> model.Image:
        raise NotImplementedError


@attr.s
class BuildahRegistry(AbstractRegistry):
    containers: tp.Set[model.Container] = attr.ib(default=attr.Factory(set))

    def _add(self, image: model.Image) -> None:
        container = model.Container(
            buildah.create_working_container(image.from_))
        self.containers.add(container)

        for layer in image.layers:
            buildah.spawn_layer(container, layer)

    def _get(self, tag: str) -> model.MaybeImage:
        # Get information from buildah registry
        return None
