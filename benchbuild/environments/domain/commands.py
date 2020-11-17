import attr

from . import declarative


def oci_compliant_name(name: str) -> str:
    """
    Convert a name to an OCI compliant name.

    For now, we just make sure it is lower-case. This is depending on
    the implementation of your container registry. podman/buildah require
    lower-case repository names for now.
    """
    # OCI Spec requires image names to be lowercase
    return name.lower()


#
# Dataclasses are perfectly valid without public methods
#


# pylint: disable=too-few-public-methods
@attr.s(frozen=True)
class Command:
    pass


@attr.s(frozen=True, hash=False)
class CreateImage(Command):
    name: str = attr.ib(converter=oci_compliant_name)
    layers: declarative.ContainerImage = attr.ib()

    def __hash__(self) -> int:
        return hash(self.name)


@attr.s(frozen=True, hash=False)
class UpdateImage(Command):
    name: str = attr.ib(converter=oci_compliant_name)
    layers: declarative.ContainerImage = attr.ib()

    def __hash__(self) -> int:
        return hash(self.name)


@attr.s(frozen=True, hash=False)
class CreateBenchbuildBase(Command):
    name: str = attr.ib(converter=oci_compliant_name, eq=True)
    layers: declarative.ContainerImage = attr.ib()

    def __hash__(self) -> int:
        return hash(self.name)


@attr.s(frozen=True, hash=False)
class RunProjectContainer(Command):
    image: str = attr.ib(converter=oci_compliant_name)
    name: str = attr.ib(converter=oci_compliant_name)

    build_dir: str = attr.ib()


# pylint: enable=too-few-public-methods
