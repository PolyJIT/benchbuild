import typing as tp

import attr

from . import model


@attr.s(frozen=True)
class Command:
    pass


@attr.s(frozen=True)
class CreateProjectImage(Command):
    name: str = attr.ib()
    layers: tp.List[model.Layer] = attr.ib()


@attr.s(frozen=True)
class CreateExperimentImage(Command):
    base: str = attr.ib()
    name: str = attr.ib()
    layers: tp.List[model.Layer] = attr.ib()


@attr.s(frozen=True)
class CreateBenchbuildBase(Command):
    name: str = attr.ib()
    layers: tp.List[model.Layer] = attr.ib()
