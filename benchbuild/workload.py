import enum
import typing as tp

from benchbuild.utils import run

WorkloadFunction = tp.Callable[[tp.Any], None]


class WorkloadProperty:  # pylint: disable=too-few-public-methods
    """
    Empty base class to encode workload properties.
    """


class EnumProperty(WorkloadProperty, enum.Enum):
    """
    Empty base classt to encode workload properties as enums.
    """


class Phase(EnumProperty):
    """
    Encode time phases of a project. There is no particular order in
    the sense that benchbuild will not run them in a particular order
    by default.
    Using proper actions that filter by Phase, you can provide an order.
    There is no dependencies between Phases, therefore, make sure that
    the build directory is in the correct state for the Phase you want to
    run.
    """
    COMPILE = 1
    RUN = 2


COMPILE = Phase.COMPILE
RUN = Phase.RUN


class Workload:  # pylint: disable=too-few-public-methods
    """
    Convert a workload function into a Workload class.

    This adds tagging and guarantees that this workload is run within
    the proper directories (build directory) with the correct config.
    """
    tags: tp.Set[WorkloadProperty]

    def __init__(self, func: WorkloadFunction, *args: WorkloadProperty) -> None:
        self.tags = set(args)

        wl_func = run.store_config(func)
        wl_func = run.in_builddir()(wl_func)

        self.__call__ = wl_func

    def __repr__(self) -> str:
        return f'Workload({self.__call__}) Properties: {self.tags}'


class Workloads:
    """
    Stores all workloads in an index.
    """
    index: tp.Set[Workload]

    def __iter__(self) -> tp.Iterator[Workload]:
        return self.index.__iter__()

    def __init__(self, *args: Workload) -> None:
        self.index = set(args)

    def add(self, func: Workload) -> None:
        self.index.add(func)

    def __repr__(self) -> str:
        return f'{self.index}'


class WorkloadMixin:
    """
    Manage workloads in a class.

    This mixin can be used to provide support for workloads in deriving
    classes. For BenchBuild that would be all descendants of Projects.

    Workloads have to be decorated using the workload.add function first.
    During class definition, this mixin will collect all decorated functions
    and add them to our set of workloads.
    """
    __workloads: tp.ClassVar[Workloads]

    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        """Create a workloads registry in the subclass only."""
        super().__init_subclass__(*args, **kwargs)

        cls.__workloads = Workloads()
        attributes = cls.__dict__.values()

        for wl_func in attributes:
            if isinstance(wl_func, Workload):
                cls.__workloads.add(wl_func)

    @classmethod
    def workloads(cls, *properties: WorkloadProperty) -> Workloads:
        """Filter our own workloads."""
        matches = [
            wl for wl in cls.__workloads
            if set(properties).intersection(wl.tags)
        ]

        return Workloads(*matches)


def define(
    *args: WorkloadProperty
) -> tp.Callable[[WorkloadFunction], Workload]:
    """
    Define a workload function.

    Decorate a member function of a project class with this and it will be
    registered as a workload for experiment actions.
    """

    def tag_workload(func: WorkloadFunction) -> Workload:
        """
        Tag the memeber function as a workload.
        """
        wl_func = Workload(func, *args)
        return wl_func

    return tag_workload
