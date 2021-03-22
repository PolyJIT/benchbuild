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
class ImageCreated(model.Event):
    name: str = attr.ib()
    from_layer: str = attr.ib()
    num_layers: int = attr.ib()


@attr.s(frozen=True)
class ContainerCreated(model.Event):
    name: str = attr.ib()
    image_id: str = attr.ib()


# pylint: enable=too-few-public-methods
