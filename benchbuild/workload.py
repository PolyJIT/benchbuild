import enum
import typing as tp

from benchbuild.utils import run

WorkloadFunction = tp.Callable[..., None]


class WorkloadProperty:  # pylint: disable=too-few-public-methods
    """
    Empty base class to encode workload properties.
    """


class EnumProperty(WorkloadProperty, enum.Enum):
    """
    Empty base class to encode workload properties as enums.
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


class Workload:
    """
    Convert a workload function into a Workload class.

    This adds tagging and guarantees that this workload is run within
    the proper directories (build directory) with the correct config.
    """
    name: str
    tags: tp.Set[WorkloadProperty]
    instance: tp.Any

    def __init__(
        self, name: str, func: WorkloadFunction, tags: tp.Set[WorkloadProperty],
        instance: tp.Any
    ) -> None:
        self.name = name
        self.tags = tags
        self.instance = instance

        # Workloads have to be constrained to a config and a build directory.
        wl_func = run.store_config(func)
        wl_func = run.in_builddir()(wl_func)

        self.func = wl_func

    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> None:
        self.func(self.instance, *args, **kwargs)

    def __repr__(self) -> str:
        return f'Workload({self.name}, {self.tags})'


class WorkloadDescriptor:
    """
    A descriptor that initializes a pre-configured workload.

    This field descriptor is set to all attributes the user has declared a
    workload. Direct accesses to the instance attribute will generate a new
    workload instance upon first use. This way we can communicate the instance
    we bind this workload to.
    """
    name: str

    def __init__(self, func: WorkloadFunction, *args: WorkloadProperty) -> None:
        self.name = ''
        self.func = func
        self.tags = set(args)

    def __set_name__(self, _, name) -> None:
        """
        Remember the attribute name.
        """
        self.name = name

    def __get__(self, instance, _) -> tp.Any:
        """
        Get or create the workload bound to this attribute name.
        """
        if self.name not in instance.__dict__:
            instance.__dict__[
                self.name
            ] = Workload(self.name, self.func, self.tags, instance)
        return instance.__dict__[self.name]

    def __set__(self, instance, value) -> None:
        """
        Bind the workload to this instance with the remembered attribute name.
        """
        instance.__dict__[self.name
                         ] = Workload(self.name, value, self.tags, instance)


Workloads = tp.Set[Workload]


class WorkloadMixin:
    """
    Manage workloads in a class.

    This mixin can be used to provide support for workloads in deriving
    classes. For BenchBuild that would be all descendants of Projects.

    Workloads have to be decorated using the workload.add function first.
    During class definition, this mixin will collect all decorated functions
    and add them to our set of workloads.
    """
    __workload_names: tp.ClassVar[tp.Set[str]]

    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        """Create a workloads registry in the subclass only."""
        super().__init_subclass__(*args, **kwargs)

        cls.__workload_names = set()

        for name, wl_func in cls.__dict__.items():
            if isinstance(wl_func, WorkloadDescriptor):
                cls.__workload_names.add(name)

    def properties(self) -> tp.Set[WorkloadProperty]:
        """
        Get all known properties.
        """
        wl_attrs = [getattr(self, name) for name in type(self).__workload_names]
        props: tp.Set[WorkloadProperty] = set()
        for func in wl_attrs:
            props.update(func.tags)
        return props

    def tags(self, name: str) -> tp.Set[WorkloadProperty]:
        """
        Get a workload's tags by name.
        """
        if name not in self.__workload_names:
            raise ValueError('Given name not a registered workload')

        func = tp.cast(Workload, getattr(self, name))
        return func.tags

    def workloads(self, *properties: WorkloadProperty) -> Workloads:
        """
        Filter our own workloads.

        The given properties are intersected with the registered workload
        properties.
        """
        wl_attrs = [getattr(self, name) for name in type(self).__workload_names]

        matches = [
            wl for wl in wl_attrs if set(properties).intersection(wl.tags)
        ]

        return set(matches)


def define(
    *args: WorkloadProperty
) -> tp.Callable[[WorkloadFunction], WorkloadDescriptor]:
    """
    Define a workload function.

    Decorate a member function of a project class with this and it will be
    registered as a workload for experiment actions.
    """

    def tag_workload(func: WorkloadFunction) -> WorkloadDescriptor:
        """
        Tag the memeber function as a workload.
        """
        wl_func = WorkloadDescriptor(func, *args)
        return wl_func

    return tag_workload
