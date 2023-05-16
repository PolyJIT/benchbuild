"""
Provide a base interface for downloadable sources.
"""
import abc
import itertools
import sys
import typing as tp
from typing import Protocol

import attr
import plumbum as pb

from benchbuild.settings import CFG

if tp.TYPE_CHECKING:
    from benchbuild.project import Project


@attr.s(frozen=True, eq=True)
class RevisionStr:  # pylint: disable=too-few-public-methods
    value: str = attr.ib()


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

    def name(self) -> str:
        return self.owner.local

    def source(self) -> 'FetchableSource':
        return self.owner

    def __str__(self) -> str:
        return str(self.version)


NestedVariants = tp.Iterable[tp.Tuple[Variant, ...]]


class Revision:
    """
    A revision captures all variants that form a single project revision.

    A project may have an arbitrary number of input sources that are
    required for it's defined workloads, e.g., test input files, optional
    dependencies, or submodules.

    BenchBuild considers each source to have different version numbers,
    encoded as "Variants". The complete set of "Variants" for a project
    then forms a project revision.
    """

    project_cls: tp.Type["Project"]
    variants: tp.Sequence[Variant]

    def __init__(
        self, project_cls: tp.Type["Project"], _primary: Variant,
        *variants: Variant
    ) -> None:
        self.project_cls = project_cls
        self.variants = [_primary] + list(variants)

    def extend(self, *variants: Variant) -> None:
        self.variants = list(self.variants) + list(variants)

    def __update_variant(self, variant: Variant) -> None:

        def __replace(elem: Variant):
            if elem.name() == variant.name():
                return variant
            return elem

        self.variants = list(map(__replace, self.variants))

    def update(self, revision: "Revision") -> None:
        for variant in revision.variants:
            self.__update_variant(variant)

    def variant_by_name(self, name: str) -> Variant:
        """
        Return the variant for the given source name.

        Args:
            name: The local name of the source.

        Returns:
            then version of the found source.
        """
        found_variants = [
            variant for variant in self.variants if variant.owner.key == name
        ]
        if len(found_variants) > 0:
            return found_variants[0]

        raise KeyError(f"Source with name {name} not found.")

    def has_variant(self, name: str) -> bool:
        """
        Check if a variant with the given source name exists.

        Args:
            name: The local name of the source.

        Returns:
            True, should a variant with the given name exists
        """
        return any(variant.owner.key == name for variant in self.variants)

    def source_by_name(self, name: str) -> 'FetchableSource':
        """
        Return the source object that matches the key.

        Args:
            name: The local name of the source.

        Returns:
            the found source object

        Raises:
            KeyError, if we cannot find the source with this name.
        """
        found_variants = [
            variant for variant in self.variants if variant.owner.key == name
        ]
        if len(found_variants) > 0:
            return found_variants[0].owner

        raise KeyError(f"Source with name {name} not found.")

    @property
    def primary(self) -> Variant:
        variants = self.sorted()
        return variants[0]

    def sorted(self) -> tp.Sequence[Variant]:
        """
        Return an ordered list of Variants from this revision.

        The order is defined by the order in the SOURCE attribute of the
        associated project class.
        """
        sources = self.project_cls.SOURCE
        sources = [src for src in sources if self.has_variant(src.key)]

        return [self.variant_by_name(src.key) for src in sources]

    def __str__(self) -> str:
        variants = self.sorted()
        return to_str(*variants)

    def __repr__(self) -> str:
        return str(self)


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

    @property
    def local(self) -> str:
        """
        The source location (path-like) after fetching it from its remote.
        """

    @property
    def remote(self) -> tp.Union[str, tp.Dict[str, str]]:
        """
        The source location in the remote location.
        """

    def fetch(self) -> pb.LocalPath:
        """
        Fetch the necessary source files into benchbuild's cache.
        """


class Expandable(Protocol):

    @property
    def is_expandable(self) -> bool:
        """
        Returns true, if this source should take part in version expansion.

        Some sources may only be treated as virtual and would not take part
        in the version expansion of an associated project.
        """

    def versions(self) -> tp.Sequence[Variant]:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """


class ContextAwareSource(Protocol):

    def is_context_free(self) -> bool:
        """
        Return, if this source needs context to evaluate it's own
        list of available versions.
        """

    def versions_with_context(self, ctx: Revision) -> tp.Sequence[Variant]:
        """
        Augment the given revision with new variants associated with this source.

        Args:
            ctx: the project revision, containing information about every
                 context-free variant.

        Returns:
            a sequence of project revisions.
        """


class ContextFreeMixin:
    """
    Make a context-free source context-aware.

    This will setup default implementations that avoids interaction with any context.
    """

    def is_context_free(self) -> bool:
        return True

    def versions_with_context(self, ctx: Revision) -> tp.Sequence[Variant]:
        raise AttributeError("Invalid use of versions with context")


class Versioned(Protocol):

    @property
    def default(self) -> Variant:
        """
        The default version for this source.
        """

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

    def versions(self) -> tp.Sequence[Variant]:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """


class FetchableSource(ContextFreeMixin):
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

    @property
    @abc.abstractmethod
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
    def versions(self) -> tp.Sequence[Variant]:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """
        raise NotImplementedError()

    def explore(self) -> tp.Sequence[Variant]:
        """
        Explore revisions of this source.

        This provides access to all revisions this source can offer.
        BenchBuild own filters will not block any revision here.

        Custom sources or source filters can opt in to block revisions
        anyways.

        Returns:
            List[str]: The list of versions to explore.
        """
        if self.is_context_free():
            return self.versions()
        return []

    @property
    def is_expandable(self) -> bool:
        return True

    @abc.abstractmethod
    def fetch(self) -> pb.LocalPath:
        """
        Fetch the necessary source files into benchbuild's cache.
        """
        raise NotImplementedError()


Sources = tp.List['FetchableSource']


class NoSource(FetchableSource):

    @property
    def default(self) -> Variant:
        return Variant(owner=self, version='None')

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        return 'None'

    def versions(self) -> tp.List[Variant]:
        return [Variant(owner=self, version='None')]

    def fetch(self) -> pb.LocalPath:
        return 'None'


def nosource() -> NoSource:
    return NoSource('NoSource', 'NoSource')


def target_prefix() -> str:
    """
    Return the prefix directory for all downloads.

    Returns:
        str: the prefix where we download everything to.
    """
    return str(CFG['tmp_dir'])


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


def secondaries(*sources: SourceT) -> tp.Sequence[SourceT]:
    """
    Return the complement to the primary source of a project.

    Returns:
        A list of all sources not considered primary.
    """
    (_, *tail) = sources
    return list(tail)


def product(*sources: Expandable) -> NestedVariants:
    """
    Return the cross product of the given sources.

    Returns:
        An iterable containing the cross product of all source variants.
    """

    siblings = [source.versions() for source in sources if source.is_expandable]
    return itertools.product(*siblings)


class BaseSource(Expandable, Versioned, ContextAwareSource, Protocol):
    """
    Composition of source protocols.
    """


class EnumeratorFn(Protocol):

    def __call__(self, *source: Expandable) -> NestedVariants:
        """
        Return an enumeration of all variants for each source.

        Returns:
            a list of version tuples, containing each possible variant.
        """


def _default_enumerator(*sources: Expandable) -> NestedVariants:
    return product(*sources)


class ContextEnumeratorFn(Protocol):

    def __call__(
        self, project_cls: tp.Type["Project"], context: Revision,
        *sources: ContextAwareSource
    ) -> tp.Sequence[Revision]:
        """
        Enumerate all revisions that are valid under the given context.
        """


def _default_caw_enumerator(
    project_cls: tp.Type["Project"], context: Revision,
    *sources: ContextAwareSource
) -> tp.Sequence[Revision]:
    """
    Transform given variant into a list of variants to check.

    This only considers the given context of all context-free sources
    per context-sensitive source.

    Args:
        context:
        *sources:
    """

    variants = [source.versions_with_context(context) for source in sources]
    variants = [var for var in variants if var]

    ret = [
        Revision(project_cls, *(list(context.variants) + list(caw_variants)))
        for caw_variants in itertools.product(*variants)
    ]
    return ret


def enumerate_revisions(
    project_cls: tp.Type["Project"],
    context_free_enumerator: EnumeratorFn = _default_enumerator,
    context_aware_enumerator: ContextEnumeratorFn = _default_caw_enumerator
) -> tp.Sequence[Revision]:
    """
    Enumerates the given sources.

    The enumeration requires two phases.
    1. A phase for all sources that do not require a context to evaluate.
    2. A phase for all sources that require a static context.
    """
    sources = project_cls.SOURCE

    context_free_sources = [
        source for source in sources if source.is_context_free()
    ]
    context_aware_sources = [
        source for source in sources if not source.is_context_free()
    ]

    revisions = context_free_enumerator(*context_free_sources)
    project_revisions = [
        Revision(project_cls, *variants) for variants in revisions
    ]

    if len(context_aware_sources) > 0:
        revs = list(
            itertools.chain(
                *(
                    context_aware_enumerator(
                        project_cls, rev, *context_aware_sources
                    ) for rev in project_revisions
                )
            )
        )
        return revs

    return project_revisions


SourceContext = tp.Dict[str, Fetchable]


def sources_as_dict(*sources: Fetchable) -> SourceContext:
    """
    Convert fetchables to a dictionary.

    The dictionary will be indexed by the Fetchable's local attribute.

    Args:
        *sources: Fetchables stored in the dictionary.
    """
    return {src.local: src for src in sources}


def revision_from_str(
    revs: tp.Sequence[RevisionStr], project_cls: tp.Type["Project"]
) -> Revision:
    """
    Create a Revision from a sequence of revision strings.

    A valid Revision can only be created, if the number of valid revision
    strings is equivalent to the number of sources.
    A valid revision string is one that has been found in the a source's
    version.
    It is required that each revision string is found in a different source
    version.

    We assume that the first source is the primary source of the revision.

    Args:
        revs: sequence of revision strings, e.g. a commit-hash.
        *sources: sources of a project.

    Returns:
        A variant context.
    """
    found: tp.List[Variant] = []
    sources = project_cls.SOURCE

    for source in sources:
        if source.is_expandable:
            found.extend([
                variant for variant in source.explore() for rev in revs
                if variant.version == rev.value
            ])

    if len(found) == 0:
        raise ValueError(f'Revisions {revs} not found in any available source.')

    return Revision(project_cls, primary(*found), *secondaries(*found))
