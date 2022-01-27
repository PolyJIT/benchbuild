"""
Extension base-classes for compile-time and run-time experiments.
"""
import logging
import typing as tp
from abc import ABCMeta

from plumbum.commands.base import BoundCommand

from benchbuild.utils import run

LOG = logging.getLogger(__name__)


class Extension(metaclass=ABCMeta):
    """An experiment functor to implement composable experiments.

    An experiment extension is always callable with an arbitrary amount of
    arguments. The varargs component of an extension's `__call__` operator
    is fed the binary command that we currently execute and all arguments
    to the binary.
    Any customization necessary for the extension (e.g, dynamic configuration
    options) has to be passed by keyword argument.

    Args:
        *extensions: Variable length list of child extensions we manage.
        config (:obj:`dict`, optional): Dictionary of name value pairs to be
            stored for this extension.

    Attributes:
        next_extensions: Variable length list of child extensions we manage.
        config (:obj:`dict`, optional): Dictionary of name value pairs to be
            stored for this extension.
    """

    def __init__(
        self,
        *extensions: 'Extension',
        config: tp.Optional[tp.Dict[str, str]] = None,
        **kwargs: tp.Any
    ):
        """Initialize an extension with an arbitrary number of children."""
        del kwargs
        self.next_extensions = extensions
        self.config = config

    def call_next(self, *args: tp.Any,
                  **kwargs: tp.Any) -> tp.List[run.RunInfo]:
        """Call all child extensions with the given arguments.

        This calls all child extensions and collects the results for
        our own parent. Use this to control the execution of your
        nested extensions from your own extension.

        Returns:
            :obj:`list` of :obj:`RunInfo`: A list of collected
                results of our child extensions.
        """
        all_results = []
        for ext in self.next_extensions:
            LOG.debug("  %s ", ext)
            results = ext(*args, **kwargs)
            LOG.debug("  %s => %s", ext, results)
            if results is None:
                LOG.warning("No result from: %s", ext)
                continue
            result_list = []
            if isinstance(results, tp.Iterable):
                result_list.extend(results)
            else:
                result_list.append(results)
            all_results.extend(result_list)

        return all_results

    def __lshift__(self, rhs: 'Extension') -> 'Extension':
        rhs.next_extensions = [self]
        return rhs

    def print(self, indent: int = 0) -> None:
        """Print a structural view of the registered extensions."""
        LOG.info("%s:: %s", indent * " ", self.__class__)
        for ext in self.next_extensions:
            ext.print(indent=indent + 2)

    def __call__(self, command: BoundCommand, *args: str,
                 **kwargs: tp.Any) -> tp.List[run.RunInfo]:
        return self.call_next(*args, **kwargs)

    def __str__(self) -> str:
        return "Extension"


class ExtensionRequired(ValueError):
    pass


class MissingExtension(Extension):
    """
    Hard fail at runtime, when the user forgets to set an extension.

    This raises an exception as soon as a user forgets to provide an extension
    for a project from the experiment.

    This should be the earliest possible moment to fail, without restricting
    existing old experiments.
    """

    def __call__(self, *args, **kwargs) -> tp.List[run.RunInfo]:
        raise ExtensionRequired()
