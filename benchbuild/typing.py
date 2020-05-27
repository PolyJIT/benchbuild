"""
"""
from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Callable, Dict, Iterable, List, Optional, Type, Union

ActionResult = Any
ExperimentAction = Callable[[], ActionResult]


class Variant:
    owner: Any
    version: str


VariantTuple = Iterable[Variant]
VariantContext = Dict[str, Variant]


class Source(ABC):

    @abstractproperty
    def default(self) -> Variant:
        """
        The default version for this source.
        """
        return NotImplemented

    @abstractmethod
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
        return NotImplemented

    @abstractmethod
    def versions(self) -> List[Variant]:
        """
        List all available versions of this source.

        Returns:
            List[str]: The list of all available versions.
        """
        return NotImplemented


class Project:
    __slots__ = ()

    NAME: str
    GROUP: str
    DOMAIN: str
    SOURCE: List[Source]

    @abstractmethod
    def run_test(self) -> None:
        return NotImplemented

    @abstractmethod
    def run(self) -> None:
        return NotImplemented

    @abstractmethod
    def clean(self) -> None:
        return NotImplemented

    @abstractmethod
    def clone(self) -> 'Project':
        return NotImplemented

    @abstractmethod
    def compile(self) -> None:
        return NotImplemented

    @abstractproperty
    def id(self) -> str:
        return NotImplemented

    @abstractmethod
    def prepare(self) -> None:
        return NotImplemented

    @abstractmethod
    def redirect(self) -> None:
        return NotImplemented

    @abstractmethod
    def source_of(self, name: str) -> Optional[str]:
        return NotImplemented

    @abstractmethod
    def version_of(self, name: str) -> Optional[str]:
        return NotImplemented


ProjectT = Type[Project]


class Experiment:
    __slots__ = ()

    @abstractmethod
    def actions_for_project(self, project: Project):
        return NotImplemented

    @abstractmethod
    def actions(self) -> List[ExperimentAction]:
        return NotImplemented

    @abstractmethod
    def sample(self, prj_cls: ProjectT, versions: List[str]) -> List[str]:
        return NotImplemented


ExperimentT = Type[Experiment]

CommandFunc = Callable[[], Union[str, None]]
CallChain = List[CommandFunc]
