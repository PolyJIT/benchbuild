"""
Provide a base interface for downloadable sources.
"""
import abc
from typing import List, Mapping, Union

import attr

from benchbuild.settings import CFG

class ISource(abc.ABC):
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
class BaseSource(ISource):
    """
    Base class for downloadable sources.
    """

    local: str = attr.ib(kw_only=True)
    remote: Union[str, Mapping[str, str]] = attr.ib(kw_only=True)

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

def target_prefix() -> str:
    """
    Return the prefix directory for all downloads.

    Returns:
        str: the prefix where we download everything to.
    """
    return str(CFG['tmp_dir'])
