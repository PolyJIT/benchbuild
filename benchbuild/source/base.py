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

    def __str__(self) -> str:
        return str(self.version)


NestedVariants = tp.Iterable[tp.Tuple[Variant, ...]]


class ProjectRevision:
    project: "Project"
    variants: tp.Sequence[Variant]

    def __init__(
        self, project: "Project", primary: Variant, *vars: Variant
    ) -> None:
        self.project = project
        self.variants = [primary] + list(vars)

        assert project.primary_source

    def extend(self, *variants: Variant) -> None:
        self.variants = list(self.variants) + list(variants)

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
        return self.variants[0]

    def __str__(self) -> str:
        name = self.project.name
        variant_str = to_str(*self.variants)

        return f"{name} version: ({variant_str})"

    def __repr__(self) -> str:
        return str(self)


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

    def versions(self) -> tp.Iterable[Variant]:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """


class ContextAwareSource(Expandable):

    @property
    def is_context_free(self) -> bool:
        """
        Return, if this source needs context to evaluate it's own list of available versions.
        """

    def versions_with_context(self, ctx: ProjectRevision) -> NestedVariants:
        """
        Augment the given revision with new variants associated with this source.

        Args:
            ctx: the project revision, containing information about every context-free variant.

        Returns:
            a sequence of project revisions.
        """


class ContextFreeMixin:
    """
    Make a context-free source context-aware.

    This will setup default implementations that avoids interaction with any context.
    """

    @property
    def is_context_free(self) -> bool:
        return True

    def versions_with_context(self, ctx: ProjectRevision) -> NestedVariants:
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

    @property
    def versions(self) -> tp.Iterable[Variant]:
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
    def versions(self) -> tp.List[Variant]:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """
        raise NotImplementedError()

    def explore(self) -> tp.Iterable[Variant]:
        """
        Explore revisions of this source.

        This provides access to all revisions this source can offer.
        BenchBuild own filters will not block any revision here.

        Custom sources or source filters can opt in to block revisions
        anyways.

        Returns:
            List[str]: The list of versions to explore.
        """
        return self.versions()

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

    def __call__(self, context: ProjectRevision,
                 *sources: ContextAwareSource) -> tp.Sequence[ProjectRevision]:
        """
        """


def _default_caw_enumerator(
    context: ProjectRevision, *sources: ContextAwareSource
) -> tp.Sequence[ProjectRevision]:
    """
    Transform given variant into a list of variants to check.

    This only considers the given context of all context-free sources per context-sensitive source.

    Args:
        context:
        *sources:
    """

    variants = [source.versions_with_context(context) for source in sources]
    return [
        ProjectRevision(
            context.project, *(list(context.variants) + list(caw_variants))
        ) for caw_variants in itertools.product(*variants)
    ]


def enumerate(
    project: "Project",
    *sources: ContextAwareSource,
    context_free_enumerator: EnumeratorFn = _default_enumerator,
    context_aware_enumerator: ContextEnumeratorFn = _default_caw_enumerator
) -> tp.Sequence[ProjectRevision]:
    """
    Enumerates the given sources.

    The enumeration requires two phases.
    1. A phase for all sources that do not require a context to evaluate.
    2. A phase for all sources that require a static context.
    """
    context_free_sources = [
        source for source in sources if source.is_context_free
    ]
    context_aware_sources = [
        source for source in sources if not source.is_context_free
    ]

    revisions = context_free_enumerator(*context_free_sources)
    project_revisions = [
        ProjectRevision(project, *variants) for variants in revisions
    ]
    if len(context_aware_sources) > 0:
        return list(
            *itertools.chain(
                context_aware_enumerator(rev, *context_aware_sources)
                for rev in project_revisions
            )
        )

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


def context_from_revisions(
    revs: tp.Sequence[RevisionStr], *sources: FetchableSource
) -> VariantContext:
    """
    Create a VariantContext from a sequence of revision strings.

    A valid VariantContext can only be created, if the number of valid revision
    strings is equivalent to the number of sources.
    A valid revision string is one that has been found in the a source's
    version.
    It is required that each revision string is found in a different source
    version.

    Args:
        revs: sequence of revision strings, e.g. a commit-hash.
        *sources: sources of a project.

    Returns:
        A variant context.
    """
    found: tp.List[Variant] = []
    for source in sources:
        if source.is_expandable:
            found.extend([
                variant for variant in source.explore() for rev in revs
                if variant.version == rev.value
            ])

    if len(found) == 0:
        raise ValueError(f'Revisions {revs} not found in any available source.')

    return context(*found)
