import attr


@attr.s
class Event:
    pass


@attr.s(frozen=True)
class LayerCreated(Event):
    name: str = attr.ib()


@attr.s(frozen=True)
class ImageCreated(Event):
    name: str
