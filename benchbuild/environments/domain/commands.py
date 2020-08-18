import typing as tp

import attr


@attr.s(frozen=True)
class Command:
    pass


@attr.s(frozen=True)
class LayerCommand:
    """BaseClass for environment layer commands."""


@attr.s(frozen=True)
class CreateProjectImage(Command):
    name: str = attr.ib()
    layers: tp.List[LayerCommand] = attr.ib()


@attr.s(frozen=True)
class CreateExperimentImage(Command):
    base: str = attr.ib()
    name: str = attr.ib()
    layers: tp.List[LayerCommand] = attr.ib()


@attr.s(frozen=True)
class CreateFromLayer(LayerCommand):
    base: str = attr.ib()


@attr.s(frozen=True)
class CreateAddLayer(LayerCommand):
    files: tp.Iterable[str] = attr.ib()
    destination: str = attr.ib()


@attr.s(frozen=True)
class CreateCopyLayer(LayerCommand):
    files: tp.Iterable[str] = attr.ib()
    destination: str = attr.ib()


@attr.s(frozen=True)
class CreateRunLayer(LayerCommand):
    command: str = attr.ib()
    args: tp.Iterable[str] = attr.ib()


@attr.s(frozen=True)
class CreateContext(LayerCommand):
    func: tp.Callable[[], None] = attr.ib()


@attr.s(frozen=True)
class ClearContext(LayerCommand):
    func: tp.Callable[[], None] = attr.ib()


@attr.s(frozen=True)
class CreateConfigLayer(LayerCommand):
    flags: tp.Iterable[str] = attr.ib()
