import attr

from . import declarative


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
class RunContainer(Command):
    image: str = attr.ib()
    name: str = attr.ib()
