import logging
import typing as tp
from enum import Enum
import copy
import abc
import attr

from benchbuild.settings import CFG

LOG = logging.getLogger(__name__)

SlurmOptionSubType = tp.TypeVar("SlurmOptionSubType", bound='SlurmOption')


@attr.s
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


@attr.s
class CoresPerSocket(SlurmOption):
    """
    Restrict node selection to nodes with at least the specified number of
    cores per socket. See additional information under -B option above when
    task/affinity plugin is enabled.
    """
    """ Number of cores required per socket. """
    cores: int = attr.ib()

    def to_slurm_cli_opt(self) -> str:
        return f"--cores-per-socket={self.cores}"

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


@attr.s
class Niceness(SlurmOption):
    """
    Run the job with an adjusted scheduling priority within Slurm. With no
    adjustment value the scheduling priority is decreased by 100. A negative
    nice value increases the priority, otherwise decreases it. The adjustment
    range is +/- 2147483645. Only privileged users can specify a negative
    adjustment.
    """
    niceness: int = attr.ib()

    def to_slurm_cli_opt(self) -> str:
        return f"--nice={self.niceness}"

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


@attr.s
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
            return str(self.value)

    hints: tp.Set[SlurmHints] = attr.ib()

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


class Time(SlurmOption):
    """
    Set a limit on the total run time of the job allocation.

    A time limit of zero requests that no time limit be imposed. Acceptable
    time formats include "minutes", "minutes:seconds", "hours:minutes:seconds",
    "days-hours", "days-hours:minutes" and "days-hours:minutes:seconds".
    """
    def __init__(self, time_specifier: str) -> None:
        self.__timelimit = self._convert_to_time_tuple(time_specifier)

    @property
    def timelimit(self) -> tp.Tuple[int, int, int, int]:
        return self.__timelimit

    def to_slurm_time_format(self) -> str:
        """
        Converst Time option into slurm compatible time format.
        """
        days = self.timelimit[0]
        hours = self.timelimit[1]
        minutes = self.timelimit[2]
        seconds = self.timelimit[3]
        tmp_str = ""
        if days > 0:
            tmp_str += f"{days}-{hours:02d}"
            if minutes > 0 or seconds > 0:
                tmp_str += f":{minutes:02d}"
            if seconds > 0:
                tmp_str += f":{seconds:02d}"
        else:
            if hours > 0:
                tmp_str += f"{hours}"
                tmp_str += f":{minutes:02d}"
                tmp_str += f":{seconds:02d}"
            else:
                tmp_str += f"{minutes}"
                if seconds > 0:
                    tmp_str += f":{seconds:02d}"

        return tmp_str

    def to_slurm_cli_opt(self) -> str:
        return f"--time={self.to_slurm_time_format()}"

    def __str__(self) -> str:
        return f"Timelimit: {self.timelimit}"

    def __repr__(self) -> str:
        return f"Time ({str(self)})"

    def __lt__(self, other) -> bool:
        return self.timelimit < other.timelimit

    @classmethod
    def merge_requirements(cls, lhs_option: 'Time',
                           rhs_option: 'Time') -> 'Time':
        """
        Merge the requirements of the same type together.
        """
        if lhs_option < rhs_option:
            return copy.deepcopy(lhs_option)
        return copy.deepcopy(rhs_option)

    @staticmethod
    def _convert_to_time_tuple(
            time_specifier: str) -> tp.Tuple[int, int, int, int]:
        """
        Convert slurm time specifier to tuple.

        Returns:
            time tuple with (days, hours, minutes, seconds)

        >>> Time._convert_to_time_tuple("4")
        (0, 0, 4, 0)
        >>> Time._convert_to_time_tuple("4:2")
        (0, 0, 4, 2)
        >>> Time._convert_to_time_tuple("8:4:2")
        (0, 8, 4, 2)
        >>> Time._convert_to_time_tuple("16-8")
        (16, 8, 0, 0)
        >>> Time._convert_to_time_tuple("16-8:4")
        (16, 8, 4, 0)
        >>> Time._convert_to_time_tuple("16-8:4:2")
        (16, 8, 4, 2)
        """
        days = 0
        hours = 0
        minutes = 0
        seconds = 0

        if time_specifier.count('-'):
            with_days = True
            days = int(time_specifier.split('-')[0])
            time_specifier = time_specifier.split('-')[1]
        else:
            with_days = False

        num_colon = time_specifier.count(':')

        if num_colon == 0:
            if with_days:
                hours = int(time_specifier)
            else:
                minutes = int(time_specifier)
        elif num_colon == 1:
            if with_days:
                hours = int(time_specifier.split(':')[0])
                minutes = int(time_specifier.split(':')[1])
            else:
                minutes = int(time_specifier.split(':')[0])
                seconds = int(time_specifier.split(':')[1])
        elif num_colon == 2:
            hours = int(time_specifier.split(':')[0])
            minutes = int(time_specifier.split(':')[1])
            seconds = int(time_specifier.split(':')[2])

        return (days, hours, minutes, seconds)


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

    slurm_options.append(Time(str(CFG['slurm']['timelimit'])))
    slurm_options.append(Niceness(int(CFG['slurm']['nice'])))

    return slurm_options
