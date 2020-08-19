import typing as tp

import attr

from . import declarative


@attr.s(frozen=True)
class Command:
    pass


@attr.s(frozen=True)
class CreateImage(Command):
    name: str = attr.ib()
    layers: declarative.ContainerImage = attr.ib()


@attr.s(frozen=True)
class UpdateImage(Command):
    name: str = attr.ib()
    layers: declarative.ContainerImage = attr.ib()


@attr.s(frozen=True)
class CreateBenchbuildBase(Command):
    name: str = attr.ib()
    layers: declarative.ContainerImage = attr.ib()
