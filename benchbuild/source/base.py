"""
Provide a base interface for downloadable sources.
"""
import abc
import itertools
import sys
import typing as tp

import attr
import plumbum as pb

from benchbuild.settings import CFG

if sys.version_info <= (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol

NestedVariants = tp.Iterable[tp.Tuple[tp.Any, ...]]


@attr.s(frozen=True, eq=True)
class Variant:
    """
    Provide a 'string'-like wrapper around source version information.

    Use this, whenever you need a 'version' string somewhere in benchbuild.
    In terms of output/logging or use as program arguments, this should not
    carry more semantics than a simple version string.

    However, this wrapper is linked to its 'owner'. The owner serves as
    the back-reference to the source code where it originated from.

    This can serve as a 'hook' to deal with version information the
    same way as a program variant like a specific configuraiton.
    """

    owner: 'FetchableSource' = attr.ib(eq=False, repr=False)
    version: str = attr.ib()

    def __str__(self) -> str:
        return str(self.version)


VariantContext = tp.Dict[str, Variant]


def context(*variants: Variant) -> VariantContext:
    """
    Convert an arbitrary number of variants into a VariantContext.

    A variant context provides an index of local source references to
    a given variant. You want to use this to access a known source component
    given variant only a variant.

    """
    return {var.owner.key: var for var in variants}


def to_str(*variants: Variant) -> str:
    """
    Convert an arbitrary number of variants into their string representation.

    Returns:
        string representation of all input variants joined by ','.
    """
    return ",".join([str(i) for i in variants])


class Fetchable(Protocol):

    @property
    def key(self) -> str:
        """
        Return the source's key property.

        This provides you with a key component that identifes a single source.
        It should (no guarantee) be unique among all sources for this project.

        While this make no further assumption, but a good candidate is a
        file-system name/path.
        """
        ...

    @property
    def local(self) -> str:
        """
        The source location (path-like) after fetching it from its remote.
        """
        ...

    @property
    def remote(self) -> tp.Union[str, tp.Dict[str, str]]:
        """
        The source location in the remote location.
        """
        ...


class Expandable(Protocol):

    @property
    def is_expandable(self) -> bool:
        """
        Returns true, if this source should take part in version expansion.

        Some sources may only be treated as virtual and would not take part
        in the version expansion of an associated project.
        """
        ...

    def versions(self) -> tp.Iterable[Variant]:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """
        ...


class Versioned(Protocol):

    @property
    def default(self) -> Variant:
        """
        The default version for this source.
        """
        ...

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        """
        Fetch the requested version and place it in the target_dir

        Args:
            target_dir (str):
                The filesystem path where the version should be placed in.
            version (str):
                The version that should be fetched from the local cache.

        Returns:
            str: [description]
        """
        ...

    @property
    def versions(self) -> tp.Iterable[Variant]:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """
        ...


class FetchableSource(Fetchable, Expandable, Versioned):
    """
    Base class for fetchable sources.

    Subclasses have to provide the following protocols:
      - Expandable
      - Fetchable
      - Versioned
    """

    _local: str
    _remote: tp.Union[str, tp.Dict[str, str]]

    def __init__(self, local: str, remote: tp.Union[str, tp.Dict[str, str]]):
        super().__init__()

        self._local = local
        self._remote = remote

    @property
    def local(self) -> str:
        return self._local

    @property
    def remote(self) -> tp.Union[str, tp.Dict[str, str]]:
        return self._remote

    @property
    def key(self) -> str:
        return self.local

    @abc.abstractproperty
    def default(self) -> Variant:
        """
        The default version for this source.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        """
        Fetch the requested version and place it in the target_dir

        Args:
            target_dir (str):
                The filesystem path where the version should be placed in.
            version (str):
                The version that should be fetched from the local cache.

        Returns:
            str: [description]
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def versions(self) -> tp.Iterable[Variant]:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """
        raise NotImplementedError()

    @property
    def is_expandable(self) -> bool:
        return True


Sources = tp.List['FetchableSource']


class NoSource(FetchableSource):

    @property
    def default(self) -> Variant:
        return Variant(owner=self, version='None')

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        return 'None'

    def versions(self) -> tp.List[Variant]:
        return [Variant(owner=self, version='None')]


def nosource() -> NoSource:
    return NoSource('NoSource', 'NoSource')


def target_prefix() -> str:
    """
    Return the prefix directory for all downloads.

    Returns:
        str: the prefix where we download everything to.
    """
    return str(CFG['tmp_dir'])


def default(*sources: Versioned) -> VariantContext:
    """
    Return the collective 'default' version for the given sources.

    Returns:
        a variant context containing all default variants for the sources.
    """
    first = [src.default for src in sources]
    return context(*first)


SourceT = tp.TypeVar('SourceT')


def primary(*sources: SourceT) -> SourceT:
    """
    Return the implicit 'main' source of a project.

    We define the main source as the first source listed in a project.

    If you define a new project and rely on the existence of a 'main'
    source code repository, make sure to define it as the first one.
    """
    (head, *_) = sources
    return head


def product(*sources: Expandable) -> NestedVariants:
    """
    Return the cross product of the given sources.

    Returns:
        An iterable containing the cross product of all source variants.
    """
    siblings = [source.versions() for source in sources if source.is_expandable]
    return itertools.product(*siblings)


SourceContext = tp.Dict[str, Fetchable]


def sources_as_dict(*sources: Fetchable) -> SourceContext:
    """
    Convert fetchables to a dictionary.

    The dictionary will be indexed by the Fetchable's local attribute.

    Args:
        *sources: Fetchables stored in the dictionary.
    """
    return {src.local: src for src in sources}
