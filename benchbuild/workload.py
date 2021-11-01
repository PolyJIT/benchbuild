import enum
import typing as tp

from benchbuild.utils import run

WorkloadFunction = tp.Callable[[tp.Any], None]


class Phase(enum.Enum):
    COMPILE = 1
    RUN = 2


class WorkloadMixin:

    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        """Create a workloads registry in the subclass only."""

        # Python 3.6's dict is insertion ordered by default.
        cls.workloads: tp.Dict[WorkloadFunction, None] = {}

        super().__init_subclass__(*args, **kwargs)

    @classmethod
    def workload(cls, func: WorkloadFunction) -> WorkloadFunction:
        """Register a new workload in the subclass."""
        wl_func = run.store_config(func)
        wl_func = run.in_builddir()(wl_func)

        cls.workloads[wl_func] = None

        return wl_func

    @classmethod
    def phase(cls, tag: Phase) -> tp.Any:
        """
        Tag a workload function with the given phase tag.

        Args:
            tag - The tag to add to the workload function.

        Returns:
            The decorated workload function.
        """

        def tag_workload(func: WorkloadFunction) -> WorkloadFunction:
            if func not in cls.workloads:
                func = cls.workload(func)

            if not hasattr(func, 'phases'):
                func.phases = set()
            func.phases.add(tag)
            return func

        return tag_workload

    def by_phase(self, tag: Phase) -> tp.List[WorkloadFunction]:
        all_phases = self.workloads.keys()

        return [
            p for p in all_phases if hasattr(p, 'phases') and tag in p.phases
        ]
