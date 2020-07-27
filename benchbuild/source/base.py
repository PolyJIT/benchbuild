"""
Provide a base interface for downloadable sources.
"""
import abc
import itertools
import typing as tp

import attr
import plumbum as pb

from benchbuild.settings import CFG

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

    owner: 'BaseSource' = attr.ib(eq=False, repr=False)
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


class ISource(abc.ABC):

    @abc.abstractproperty
    def local(self) -> str:
        """
        The source location (path-like) after fetching it from its remote.
        """

    @abc.abstractproperty
    def remote(self) -> tp.Union[str, tp.Dict[str, str]]:
        """
        The source location in the remote location.
        """

    @abc.abstractproperty
    def key(self) -> str:
        """
        Return the source's key property.

        This provides you with a key component that identifes a single source.
        It should (no guarantee) be unique among all sources for this project.

        While this make no further assumption, but a good candidate is a
        file-system name/path.
        """

    @abc.abstractproperty
    def default(self) -> Variant:
        """
        The default version for this source.
        """

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

    @abc.abstractmethod
    def versions(self) -> tp.Iterable[Variant]:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """


@attr.s
class BaseSource(ISource):
    """
    Base class for downloadable sources.
    """

    _local: str = attr.ib()
    _remote: tp.Union[str, tp.Dict[str, str]] = attr.ib()

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

    @abc.abstractmethod
    def versions(self) -> tp.Iterable[Variant]:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """


Sources = tp.List['BaseSource']


@attr.s
class NoSource(BaseSource):

    @property
    def default(self) -> Variant:
        return Variant(owner=self, version='None')

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        return 'None'

    def versions(self) -> tp.List[Variant]:
        return [Variant(owner=self, version='None')]


def nosource() -> NoSource:
    return NoSource(local='NoSource', remote='NoSource')


def target_prefix() -> str:
    """
    Return the prefix directory for all downloads.

    Returns:
        str: the prefix where we download everything to.
    """
    return str(CFG['tmp_dir'])


def default(*sources: BaseSource) -> VariantContext:
    """
    Return the collective 'default' version for the given sources.

    Returns:
        a variant context containing all default variants for the sources.
    """
    first = [src.default for src in sources]
    return context(*first)


def primary(source: BaseSource, *sources: BaseSource) -> BaseSource:
    """
    Return the implicit 'main' source of a project.

    We define the main source as the first source listed in a project.

    If you define a new project and rely on the existence of a 'main'
    source code repository, make sure to define it as the first one.
    """
    del sources

    return source


def product(*sources: BaseSource) -> NestedVariants:
    """
    Return the cross product of the given sources.

    Returns:
        An iterable containing the cross product of all source variants.
    """
    siblings = [source.versions() for source in sources]
    return itertools.product(*siblings)
