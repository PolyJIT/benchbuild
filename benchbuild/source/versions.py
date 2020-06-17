import abc
import itertools
from typing import List, Union

import attr

from .base import ISource


@attr.s
class BaseVersionGroup(ISource):
    children: List[ISource] = attr.ib()

    @abc.abstractmethod
    def version(self, target_dir: str, version: str) -> str:
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
    def versions(self) -> List['Variant']:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """


@attr.s
class BaseVersionFilter(ISource):
    child: ISource = attr.ib()

    def fetch(self) -> Union[List[str], str]:
        """
        Delegate all calls to fetch to the wrapped child object.

        Returns:
            List[str]:
                A list of generated source files in the local target directory.
        """
        return self.child.fetch()

    def fetch_version(self, target_dir: str, version: str) -> str:
        """
        Delegate all calls to fetch_version to the wrapped child object.

        Args:
            target_dir (str):
                The filesystem path where the version should be placed in.
            version (str):
                The version that should be fetched from the local cache.

        Returns:
            str: [description]
        """
        return self.child.fetch_version(target_dir, version)

    @abc.abstractmethod
    def versions(self) -> List['Version']:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """


@attr.s
class CartesianProduct(BaseVersionGroup):

    def version(self, target_dir: str, version: List[str]) -> str:
        ret = []
        for i, vers in enumerate(version):
            child = self.children[i]
            ret.append(child.version(target_dir, vers))

        return str(ret)

    def versions(self):
        child_versions = [child.versions() for child in self.children]
        return itertools.product(*child_versions)


def product(*variants):
    """
    Generate cartesian product of all given variants.

    Returns:
        CartesianProduct: The cartesian product of all given variants
    """
    return CartesianProduct(children=variants)
