import abc
import typing as tp

import plumbum as pb

from . import base


class BaseVersionGroup(base.Versioned):

    def __init__(self, children: tp.List[base.FetchableSource]):
        super().__init__()

        self.children = children

    @property
    def local(self) -> str:
        raise NotImplementedError('Does not make sense on a group of sources')

    @property
    def remote(self) -> tp.Union[str, tp.Dict[str, str]]:
        raise NotImplementedError('Does not make sense on a group of sources')

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
    def versions(self) -> tp.List[base.Variant]:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """


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


class SingleVersionFilter(BaseVersionFilter):
    """
    A simple single versions only filter.
    """

    def __init__(self, child: base.FetchableSource, filter_version: str):
        super().__init__(child)
        self.filter_version = filter_version

    def versions(self) -> tp.List[base.Variant]:
        return [
            v for v in self.child.versions() if str(v) == self.filter_version
        ]
