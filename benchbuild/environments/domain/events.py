import attr

from . import model

#
# Dataclasses are perfectly valid without public methods
#


# pylint: disable=too-few-public-methods
@attr.s(frozen=True)
class LayerCreated(model.Event):
    name: str = attr.ib()
    container_id: str = attr.ib()
    image_tag: str = attr.ib()


@attr.s(frozen=True)
class LayerCreationFailed(model.Event):
    name: str = attr.ib()
    image_tag: str = attr.ib()
    message: str = attr.ib()


@attr.s(frozen=True)
class ImageCreated(model.Event):
    name: str = attr.ib()
    from_layer: str = attr.ib()
    num_layers: int = attr.ib()


@attr.s(frozen=True)
class ImageCreationFailed(model.Event):
    name: str = attr.ib()
    reason: str = attr.ib()


@attr.s(frozen=True)
class ContainerCreated(model.Event):
    name: str = attr.ib()
    image_id: str = attr.ib()


@attr.s(frozen=True)
class ContainerStartFailed(model.Event):
    name: str = attr.ib()
    container_id: str = attr.ib()
    message: str = attr.ib()


@attr.s(frozen=True)
class ContainerStarted(model.Event):
    container_id: str = attr.ib()


@attr.s(frozen=True)
class DebugImageKept(model.Event):
    image_name: str = attr.ib()
    failed_image_name: str = attr.ib()
    failed_layer: str = attr.ib()


# pylint: enable=too-few-public-methods
