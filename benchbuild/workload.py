import enum
import typing as tp
from types import MethodType

from benchbuild.utils import run

WorkloadFunction = tp.Callable[[tp.Any], None]


class WorkloadProperty:  # pylint: disable=too-few-public-methods
    """
    Empty base class to encode workload properties.
    """


class EnumProperty(WorkloadProperty, enum.Enum):
    """
    Encode workload properties as enums.
    """


class Phase(EnumProperty):
    COMPILE = 1
    RUN = 2


COMPILE = Phase.COMPILE
RUN = Phase.RUN


class Workloads:
    """
    Stores all workloads in an index.
    """
    index: tp.Set[WorkloadFunction]

    # TODO: Misses iterable protocol

    def __init__(self) -> None:
        self.index = set()

    def add(self, func: WorkloadFunction) -> None:
        self.index.add(func)


class WorkloadMixin:
    workloads: tp.ClassVar[Workloads]

    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        """Create a workloads registry in the subclass only."""
        super().__init_subclass__(*args, **kwargs)

        cls.workloads = Workloads()
        attributes = cls.__dict__.values()

        for wl_func in attributes:
            if isinstance(wl_func, Workload):
                cls.workloads.add(wl_func)

    @classmethod
    def filter(cls) -> Workloads:
        """Filter our own workloads."""
        return cls.workloads


class Workload:  # pylint: disable=too-few-public-methods
    tags: tp.Set[WorkloadProperty]

    def __init__(self, func: WorkloadFunction, *args: WorkloadProperty) -> None:
        self.tags = set(args)

        wl_func = run.store_config(func)
        wl_func = run.in_builddir()(wl_func)

        self.__call__ = wl_func


def add(*args: WorkloadProperty) -> tp.Callable[[WorkloadFunction], Workload]:
    """
    Add a workload function to our registry.
    """

    def tag_workload(func: WorkloadFunction) -> Workload:
        """
        Tag the memeber function as a workload.
        """
        wl_func = Workload(func, *args)
        return wl_func

    return tag_workload
