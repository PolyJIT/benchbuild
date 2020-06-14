import logging
import typing as tp
from enum import Enum
import abc

from benchbuild.settings import CFG

LOG = logging.getLogger(__name__)

SlurmOptionSubType = tp.TypeVar("SlurmOptionSubType", bound='SlurmOption')


class SlurmOption:
    """
    Base class for Slurm options.
    """
    def to_slurm_opt(self) -> str:
        """
        Converst slurm option into a script usable option string, i.e., bash
        #SBATCH option line.
        """
        return f"#SBATCH {self.to_slurm_cli_opt()}"

    @abc.abstractmethod
    def to_slurm_cli_opt(self) -> str:
        """
        Converst slurm option to command line string.
        """

    @classmethod
    @abc.abstractmethod
    def merge_requirements(
            cls: tp.Type[SlurmOptionSubType], lhs_option: SlurmOptionSubType,
            rhs_option: SlurmOptionSubType) -> SlurmOptionSubType:
        """
        Merge the requirements of the same type together.
        """
        return type(lhs_option).merge_requirements(lhs_option, rhs_option)


class CoresPerSocket(SlurmOption):
    """
    Restrict node selection to nodes with at least the specified number of
    cores per socket. See additional information under -B option above when
    task/affinity plugin is enabled.
    """
    def __init__(self, cores: int) -> None:
        self.__cores = cores

    @property
    def cores(self) -> int:
        """ Number of cores required per socket. """
        return self.__cores

    def to_slurm_cli_opt(self) -> str:
        return f"--cores-per-socket={self.cores}"

    def __str__(self) -> str:
        return f"Cores {self.cores}"

    def __repr__(self) -> str:
        return f"CoresPerSocket (Cores: {self.cores})"

    @classmethod
    def merge_requirements(cls, lhs_option: 'CoresPerSocket',
                           rhs_option: 'CoresPerSocket') -> 'CoresPerSocket':
        """
        Merge the requirements of the same type together.
        """
        return CoresPerSocket(max(lhs_option.cores, rhs_option.cores))


class Exclusive(SlurmOption):
    """
    The job allocation can not share nodes with other running jobsThe job
    allocation can not share nodes with other running jobs
    """
    def to_slurm_cli_opt(self) -> str:
        return "--exclusive"

    def __str__(self) -> str:
        return "Run Exclusive"

    def __repr__(self) -> str:
        return "Exclusive"

    @classmethod
    def merge_requirements(cls, lhs_option: 'Exclusive',
                           rhs_option: 'Exclusive') -> 'Exclusive':
        """
        Merge the requirements of the same type together.
        """
        return Exclusive()


class Niceness(SlurmOption):
    """
    Run the job with an adjusted scheduling priority within Slurm. With no
    adjustment value the scheduling priority is decreased by 100. A negative
    nice value increases the priority, otherwise decreases it. The adjustment
    range is +/- 2147483645. Only privileged users can specify a negative
    adjustment.
    """
    def __init__(self, niceness: int) -> None:
        self.__niceness = niceness

    @property
    def niceness(self) -> int:
        return self.__niceness

    def to_slurm_cli_opt(self) -> str:
        return f"--nice={self.niceness}"

    def __str__(self) -> str:
        return f"Nice: {self.niceness}"

    def __repr__(self) -> str:
        return f"Niceness (Nice: {self.niceness})"

    @classmethod
    def merge_requirements(cls, lhs_option: 'Niceness',
                           rhs_option: 'Niceness') -> 'Niceness':
        """
        Merge the requirements of the same type together.
        """
        if lhs_option.niceness != rhs_option.niceness:
            LOG.info("Multiple different slurm niceness values specifcied, "
                     "choosing the smaller value.")

        return Niceness(min(lhs_option.niceness, rhs_option.niceness))


class Hint(SlurmOption):
    """
    Bind tasks according to application hints.
        * compute_bound
            Select settings for compute bound applications: use all cores in
            each socket, one thread per core.
        * memory_bound
            Select settings for memory bound applications: use only one core
            in each socket, one thread per core.
        * [no]multithread
            [don't] use extra threads with in-core multi-threading which can
            benefit communication intensive applications. Only supported with
            the task/affinity plugin.
    """
    class SlurmHints(Enum):
        compute_bound = "compute_bound"
        memory_bound = "memory_bound"
        multithread = "multithread"
        nomultithread = "nomultithread"

        def __str__(self) -> str:
            return tp.cast(str, self.value)

    def __init__(self, hints: tp.Set[SlurmHints]) -> None:
        self.__hints = hints

    @property
    def hints(self) -> tp.Set[SlurmHints]:
        return self.__hints

    def to_slurm_cli_opt(self) -> str:
        return f"--hint={','.join(map(str, self.hints))}"

    def __str__(self) -> str:
        return f"Hints: {','.join(map(str, self.hints))}"

    def __repr__(self) -> str:
        return f"Hint ({str(self)})"

    @classmethod
    def merge_requirements(cls, lhs_option: 'Hint',
                           rhs_option: 'Hint') -> 'Hint':
        """
        Merge the requirements of the same type together.
        """
        combined_hints = set()
        combined_hints |= lhs_option.hints | rhs_option.hints

        if not cls.__hints_not_mutually_exclusive(combined_hints):
            raise ValueError(
                "Two mutally exclusive hints for slurm have be specified.")

        return Hint(combined_hints)

    @staticmethod
    def __hints_not_mutually_exclusive(hints: tp.Set[SlurmHints]) -> bool:
        """
        Checks that a list of `SlurmHints` does not include mutally exclusive
        hints.

        Returns:
            True, if no mutally exclusive hints are in the list
        """
        if (Hint.SlurmHints.compute_bound in hints
                and Hint.SlurmHints.memory_bound in hints):
            return False
        if (Hint.SlurmHints.nomultithread in hints
                and Hint.SlurmHints.multithread in hints):
            return False

        return True


def merge_slurm_options(list_1: tp.List[SlurmOption],
                        list_2: tp.List[SlurmOption]) -> tp.List[SlurmOption]:
    """
    Merged two lists of SlurmOptions into one.
    """
    merged_options: tp.Dict[tp.Type[SlurmOption], SlurmOption] = dict()

    for opt in list_1 + list_2:
        key = type(opt)
        if key in merged_options:
            current_opt = merged_options[key]
            merged_options[key] = current_opt.merge_requirements(
                current_opt, opt)
        else:
            merged_options[key] = opt

    return list(merged_options.values())


def get_slurm_options_from_config() -> tp.List[SlurmOption]:
    """
    Generates a list of `SlurmOptions` which are specified in the BenchBuild
    config.
    """
    slurm_options: tp.List[SlurmOption] = []
    if CFG['slurm']['exclusive']:
        slurm_options.append(Exclusive())

    if not CFG['slurm']['multithread']:
        slurm_options.append(Hint({Hint.SlurmHints.nomultithread}))

    slurm_options.append(Niceness(int(CFG['slurm']['nice'])))

    return slurm_options
