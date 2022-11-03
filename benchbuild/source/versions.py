import abc
import typing as tp

import plumbum as pb

from . import base


class BaseVersionFilter(base.FetchableSource):
    child: base.FetchableSource

    def __init__(self, child: base.FetchableSource):
        super().__init__(child.local, child.remote)

        self.child = child

    @property
    def default(self) -> base.Variant:
        return self.child.default

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        """
        Delegate all calls to fetch to the wrapped child object.

        Returns:
            List[str]:
                A list of generated source files in the local target directory.
        """
        return self.child.version(target_dir, version)

    @abc.abstractmethod
    def versions(self) -> tp.List[base.Variant]:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """

    def explore(self) -> tp.List[base.Variant]:
        """
        Explore all revisions of the child source.

        This bypasses the filter by default.

        Returns:
            List[str]: The list of all available versions.
        """
        return self.child.versions()

    def fetch(self) -> pb.LocalPath:
        """
        Delegate fetch call to child source.
        """
        return self.child.fetch()


class SingleVersionFilter(BaseVersionFilter):
    """
    A simple single versions only filter.
    """

    def is_context_free(self) -> bool:
        return self.child.is_context_free()

    def __init__(self, child: base.FetchableSource, filter_version: str):
        super().__init__(child)
        self.filter_version = filter_version

    def versions(self) -> tp.List[base.Variant]:
        return [
            v for v in self.child.versions() if str(v) == self.filter_version
        ]

    def versions_with_context(self,
                              ctx: base.Revision) -> tp.Sequence[base.Variant]:
        return [
            v for v in self.child.versions_with_context(ctx)
            if str(v) == self.filter_version
        ]

    def explore(self) -> tp.List[base.Variant]:
        return list(self.child.explore())
