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
class CreateBenchbuildBase(Command):
    name: str = attr.ib()
    layers: tp.List[LayerCommand] = attr.ib()
