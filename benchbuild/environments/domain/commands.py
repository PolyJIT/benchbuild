import attr

from . import declarative

#
# Dataclasses are perfectly valid without public methods
#


# pylint: disable=too-few-public-methods
@attr.s(frozen=True)
class Command:
    pass


@attr.s(frozen=True, hash=False)
class CreateImage(Command):
    name: str = attr.ib()
    layers: declarative.ContainerImage = attr.ib()

    def __hash__(self) -> int:
        return hash(self.name)


@attr.s(frozen=True, hash=False)
class UpdateImage(Command):
    name: str = attr.ib()
    layers: declarative.ContainerImage = attr.ib()

    def __hash__(self) -> int:
        return hash(self.name)


@attr.s(frozen=True, hash=False)
class CreateBenchbuildBase(Command):
    name: str = attr.ib(eq=True)
    layers: declarative.ContainerImage = attr.ib()

    def __hash__(self) -> int:
        return hash(self.name)


@attr.s(frozen=True, hash=False)
class RunProjectContainer(Command):
    image: str = attr.ib()
    name: str = attr.ib()

    build_dir: str = attr.ib()


# pylint: enable=too-few-public-methods
