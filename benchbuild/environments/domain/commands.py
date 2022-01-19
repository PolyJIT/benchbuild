import re
import typing as tp
import unicodedata

import attr

from . import declarative, model


def fs_compliant_name(name: str) -> str:
    """
    Convert a name to a valid filename.
    """
    value = str(name)
    value = unicodedata.normalize('NFKD',
                                  value).encode('ascii',
                                                'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def oci_compliant_name(name: str) -> str:
    """
    Convert a name to an OCI compliant name.

    For now, we just make sure it is lower-case. This is depending on
    the implementation of your container registry. podman/buildah require
    lower-case repository names for now.

    Args:
        name: the name to convert

    Examples:
        >>> oci_compliant_name("foo")
        'foo'
        >>> oci_compliant_name("FoO")
        'foo'
    """
    # OCI Spec requires image names to be lowercase
    return name.lower()


#
# Dataclasses are perfectly valid without public methods
#


# pylint: disable=too-few-public-methods
@attr.s(frozen=True, hash=False)
class CreateImage(model.Command):
    name: str = attr.ib(converter=oci_compliant_name)
    layers: declarative.ContainerImage = attr.ib()

    def __hash__(self) -> int:
        return hash(self.name)


@attr.s(frozen=True, hash=False)
class DeleteImage(model.Command):
    name: str = attr.ib(converter=oci_compliant_name)


@attr.s(frozen=True, hash=False)
class CreateBenchbuildBase(model.Command):
    name: str = attr.ib(converter=oci_compliant_name, eq=True)
    layers: declarative.ContainerImage = attr.ib()

    def __hash__(self) -> int:
        return hash(self.name)


@attr.s(frozen=True, hash=False)
class RunProjectContainer(model.Command):
    image: str = attr.ib(converter=oci_compliant_name)
    name: str = attr.ib(converter=oci_compliant_name)

    build_dir: str = attr.ib()
    args: tp.Sequence[str] = attr.ib(default=attr.Factory(list))


@attr.s(frozen=True, hash=False)
class ExportImage(model.Command):
    image: str = attr.ib(converter=oci_compliant_name)
    out_name: str = attr.ib()


@attr.s(frozen=True, hash=False)
class ImportImage(model.Command):
    image: str = attr.ib(converter=oci_compliant_name)
    in_path: str = attr.ib()


# pylint: enable=too-few-public-methods
