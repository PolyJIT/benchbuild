import attr


@attr.s(frozen=True)
class Event:
    pass


@attr.s(frozen=True)
class CreatingLayer(Event):
    name: str = attr.ib()
    layer: str = attr.ib()


@attr.s(frozen=True)
class LayerCreated(Event):
    name: str = attr.ib()
    layer: str = attr.ib()


@attr.s(frozen=True)
class ImageCreated(Event):
    name: str = attr.ib()
    from_layer: str = attr.ib()
    num_layers: int = attr.ib()


@attr.s(frozen=True)
class ContainerCreated(Event):
    image_id: str = attr.ib()
    name: str = attr.ib()


@attr.s(frozen=True)
class ImageCommitted(Event):
    name: str = attr.ib()


@attr.s(frozen=True)
class ImageDestroyed(Event):
    name: str = attr.ib()
