import abc
import itertools
import typing as tp

import attr
import plumbum as pb

from . import base


@attr.s
class BaseVersionGroup(base.ISource):
    children: tp.List[base.ISource] = attr.ib()

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


@attr.s
class BaseVersionFilter(base.ISource):
    child: base.ISource = attr.ib()

    @property
    def local(self) -> str:
        return self.child.local

    @property
    def remote(self) -> tp.Union[str, tp.Dict[str, str]]:
        return self.child.remote

    @property
    def key(self) -> str:
        return self.child.key

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


@attr.s
class SingleVersionFilter(BaseVersionFilter):
    """
    A simple single versions only filter.
    """
    filter_version: str = attr.ib()

    def versions(self) -> tp.List[base.Variant]:
        return [
            v for v in self.child.versions() if str(v) == self.filter_version
        ]


@attr.s
class CartesianProduct(BaseVersionGroup):

    @property
    def default(self) -> base.Variant:
        raise NotImplementedError('No default version for cartesian product')

    def version(self, target_dir: str,
                version: tp.Iterable[str]) -> pb.LocalPath:
        ret = []
        for i, vers in enumerate(version):
            child = self.children[i]
            ret.append(child.version(target_dir, vers))

        return str(ret)

    def versions(self) -> tp.List[base.Variant]:
        child_versions = [child.versions() for child in self.children]
        return list(itertools.product(*child_versions))


def product(*sources: base.ISource) -> base.ISource:
    """
    Generate cartesian product of all given variants.

    Returns:
        CartesianProduct: The cartesian product of all given variants
    """
    return CartesianProduct(children=list(sources))
