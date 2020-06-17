"""
Provide a base interface for downloadable sources.
"""
import abc
import itertools
from typing import Iterable, List, Mapping, Union

import attr

from benchbuild.settings import CFG

from . import variants


class ISource(abc.ABC):

    @abc.abstractproperty
    def default(self) -> 'benchbuild.variants.Variant':
        """
        The default version for this source.
        """

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
    def versions(self) -> Iterable['Variant']:
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

    local: str = attr.ib()
    remote: Union[str, Mapping[str, str]] = attr.ib()

    @abc.abstractproperty
    def default(self) -> 'benchbuild.variants.Variant':
        """
        The default version for this source.
        """

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
    def versions(self) -> Iterable['Variant']:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """


Sources = List['BaseSource']


@attr.s
class NoSource(BaseSource):

    @property
    def default(self):
        return variants.Variant(owner=self, version='None')

    def version(self, target_dir: str, version: str) -> str:
        return 'None'

    def versions(self) -> List['Variant']:
        return ['None']


def nosource():
    return NoSource(local='NoSource', remote='NoSource')


def target_prefix() -> str:
    """
    Return the prefix directory for all downloads.

    Returns:
        str: the prefix where we download everything to.
    """
    return str(CFG['tmp_dir'])


def default(sources: Sources) -> variants.VariantContext:
    first = [src.default for src in sources]
    return variants.context(first)


def product(sources: Sources):
    siblings = [source.versions() for source in sources]
    return itertools.product(*siblings)
