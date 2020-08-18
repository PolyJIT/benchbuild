import attr


@attr.s
class Event:
    pass


@attr.s(frozen=True)
class LayerCreated(Event):
    name: str = attr.ib()
    command: str = attr.ib()


@attr.s(frozen=True)
class ContextCreated(Event):
    context_dir: str = attr.ib()


@attr.s(frozen=True)
class ImageCreated(Event):
    name: str
