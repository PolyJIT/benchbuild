import abc
import typing as tp

import attr

from benchbuild.environments.adapters import buildah
from benchbuild.environments.domain import model


@attr.s
class AbstractRegistry(abc.ABC):
    images: tp.Set[model.Image] = attr.ib(default=attr.Factory(set))
    containers: tp.Set[model.Container] = attr.ib(default=attr.Factory(set))

    def get(self, tag: str) -> model.MaybeImage:
        image = self._get(tag)
        if image:
            self.images.add(image)
        return image

    def create(self, tag: str, layers: tp.List[model.Layer]) -> model.Container:
        container = self._create(tag, layers)
        if container:
            self.containers.add(container)
        return container

    @abc.abstractmethod
    def _create(
        self, tag: str, layers: tp.List[model.Layer]
    ) -> model.Container:
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, tag: str) -> model.Image:
        raise NotImplementedError


@attr.s
class BuildahRegistry(AbstractRegistry):

    def _get(self, tag: str) -> model.MaybeImage:
        return buildah.find_image(tag)

    def _create(
        self, tag: str, layers: tp.List[model.Layer]
    ) -> model.Container:
        from_ = [l for l in layers if isinstance(l, model.FromLayer)].pop(0)
        image = model.Image(tag, from_, layers[1:])

        container_id = buildah.create_working_container(image.from_)
        context = buildah.create_build_context()
        container = model.Container(container_id, image, context)

        return container
