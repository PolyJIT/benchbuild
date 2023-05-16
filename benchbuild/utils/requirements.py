import abc
import copy
import logging
import math
import re
import typing as tp
from enum import Enum

import attr

from benchbuild.settings import CFG

LOG = logging.getLogger(__name__)

RequirementSubType = tp.TypeVar("RequirementSubType", bound='Requirement')


@attr.s
class Requirement:
    """
    Base class for requirements.
    """

    @abc.abstractmethod
    def to_option(self) -> str:
        """
        Converts Requirement to a script options.
        """

    @abc.abstractmethod
    def to_cli_option(self) -> str:
        """
        Converts Requirement to a command line options.
        """

    @classmethod
    @abc.abstractmethod
    def merge_requirements(
        cls: tp.Type[RequirementSubType], lhs_option: RequirementSubType,
        rhs_option: RequirementSubType
    ) -> RequirementSubType:
        """
        Merge the requirements of the same type together.
        """
        return type(lhs_option).merge_requirements(lhs_option, rhs_option)


################################################################################
# Slurm Requirements                                                           #
################################################################################


class SlurmRequirement(Requirement):
    """
    Base class for slurm requirements.
    """

    def to_option(self) -> str:
        """
        Converts Requirement to a script options.
        """
        return self.to_slurm_opt()

    def to_cli_option(self) -> str:
        """
        Converts Requirement to a command line options.
        """
        return self.to_slurm_cli_opt()

    def to_slurm_opt(self) -> str:
        """
        Convert slurm option into a script usable option string, i.e., bash
        #SBATCH option line.
        """
        return f"#SBATCH {self.to_slurm_cli_opt()}"

    @abc.abstractmethod
    def to_slurm_cli_opt(self) -> str:
        """
        Convert slurm option to command line string.
        """


@attr.s
class SlurmCoresPerSocket(SlurmRequirement):
    """
    Restrict node selection to nodes with at least the specified number of
    cores per socket. See additional information under -B option in the slurm
    documentation. Only works when task/affinity plugin is enabled.
    """
    cores: int = attr.ib()

    def to_slurm_cli_opt(self) -> str:
        return f"--cores-per-socket={self.cores}"

    @classmethod
    def merge_requirements(
        cls, lhs_option: 'SlurmCoresPerSocket',
        rhs_option: 'SlurmCoresPerSocket'
    ) -> 'SlurmCoresPerSocket':
        """
        Merge the requirements of the same type together.
        """
        return SlurmCoresPerSocket(max(lhs_option.cores, rhs_option.cores))


class SlurmExclusive(SlurmRequirement):
    """
    The job allocation can not share nodes with other running jobs.
    """

    def to_slurm_cli_opt(self) -> str:
        return "--exclusive"

    def __str__(self) -> str:
        return "Run Exclusive"

    def __repr__(self) -> str:
        return "Exclusive"

    @classmethod
    def merge_requirements(
        cls, lhs_option: 'SlurmExclusive', rhs_option: 'SlurmExclusive'
    ) -> 'SlurmExclusive':
        """
        Merge the requirements of the same type together.
        """
        return SlurmExclusive()


@attr.s
class SlurmNiceness(SlurmRequirement):
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
    def merge_requirements(
        cls, lhs_option: 'SlurmNiceness', rhs_option: 'SlurmNiceness'
    ) -> 'SlurmNiceness':
        """
        Merge the requirements of the same type together.
        """
        if lhs_option.niceness != rhs_option.niceness:
            LOG.info(
                "Multiple different slurm niceness values specifcied, "
                "choosing the smaller value."
            )

        return SlurmNiceness(min(lhs_option.niceness, rhs_option.niceness))


@attr.s
class SlurmHint(SlurmRequirement):
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
    def merge_requirements(
        cls, lhs_option: 'SlurmHint', rhs_option: 'SlurmHint'
    ) -> 'SlurmHint':
        """
        Merge the requirements of the same type together.
        """
        combined_hints = set()
        combined_hints |= lhs_option.hints | rhs_option.hints

        if not cls.__hints_not_mutually_exclusive(combined_hints):
            raise ValueError(
                "Two mutally exclusive hints for slurm have be specified."
            )

        return SlurmHint(combined_hints)

    @staticmethod
    def __hints_not_mutually_exclusive(hints: tp.Set[SlurmHints]) -> bool:
        """
        Checks that a list of `SlurmHints` does not include mutally exclusive
        hints.

        Returns:
            True, if no mutally exclusive hints are in the list
        """
        if (
            SlurmHint.SlurmHints.compute_bound in hints and
            SlurmHint.SlurmHints.memory_bound in hints
        ):
            return False
        if (
            SlurmHint.SlurmHints.nomultithread in hints and
            SlurmHint.SlurmHints.multithread in hints
        ):
            return False

        return True


def _convert_to_time_tuple(time_specifier: str) -> tp.Tuple[int, int, int, int]:
    """
    Convert slurm time specifier to tuple.

    Returns:
        time tuple with (days, hours, minutes, seconds)

    Examples:
        >>> _convert_to_time_tuple("4")
        (0, 0, 4, 0)
        >>> _convert_to_time_tuple("4:2")
        (0, 0, 4, 2)
        >>> _convert_to_time_tuple("8:4:2")
        (0, 8, 4, 2)
        >>> _convert_to_time_tuple("16-8")
        (16, 8, 0, 0)
        >>> _convert_to_time_tuple("16-8:4")
        (16, 8, 4, 0)
        >>> _convert_to_time_tuple("16-8:4:2")
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


@attr.s
class SlurmTime(SlurmRequirement):
    """
    Set a limit on the total run time of the job allocation.

    A time limit of zero requests that no time limit be imposed. Acceptable
    time formats include "minutes", "minutes:seconds", "hours:minutes:seconds",
    "days-hours", "days-hours:minutes" and "days-hours:minutes:seconds".
    """
    timelimit: tp.Tuple[int, int, int,
                        int] = attr.ib(converter=_convert_to_time_tuple)

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

    @classmethod
    def merge_requirements(
        cls, lhs_option: 'SlurmTime', rhs_option: 'SlurmTime'
    ) -> 'SlurmTime':
        """
        Merge the requirements of the same type together.
        """
        if lhs_option < rhs_option:
            return copy.deepcopy(lhs_option)
        return copy.deepcopy(rhs_option)


def _get_byte_size_factor(byte_suffix: str) -> int:
    """
    Returns the factor for a specific bytesize.
    """
    byte_suffix = byte_suffix.lower()
    if byte_suffix == "b":
        return 1
    if byte_suffix in ("k", "kb"):
        return 1024
    if byte_suffix in ("m", "mb"):
        return 1024 * 1024
    if byte_suffix in ("g", "gb"):
        return 1024 * 1024 * 1024
    if byte_suffix in ("t", "tb"):
        return 1024 * 1024 * 1024 * 1024

    raise ValueError("Unsupported byte suffix")


_BYTE_RGX = re.compile(r"(?P<size>\d*)(?P<byte_suffix>.*)")


def _to_bytes(byte_str: str) -> int:
    """
    >>> _to_bytes("4B")
    4
    >>> _to_bytes("4MB")
    4194304
    >>> _to_bytes("10G")
    10737418240
    """
    if (match := _BYTE_RGX.search(byte_str)):
        size = int(match.group("size"))
        byte_suffix = match.group("byte_suffix")
        return size * _get_byte_size_factor(byte_suffix)

    raise ValueError("Passed byte size was wrongly formatted")


def _to_biggests_byte_size(num_bytes: int) -> tp.Tuple[int, str]:
    """
    >>> _to_biggests_byte_size(4)
    (4, 'B')
    >>> _to_biggests_byte_size(4194304)
    (4, 'M')
    >>> _to_biggests_byte_size(4194305)
    (5, 'M')
    >>> _to_biggests_byte_size(10737418240)
    (10, 'G')
    >>> _to_biggests_byte_size(1099511627776)
    (1, 'T')
    """
    if num_bytes >= _get_byte_size_factor("TB"):
        return (math.ceil(num_bytes / _get_byte_size_factor("TB")), "T")
    if num_bytes >= _get_byte_size_factor("GB"):
        return (math.ceil(num_bytes / _get_byte_size_factor("GB")), "G")
    if num_bytes >= _get_byte_size_factor("MB"):
        return (math.ceil(num_bytes / _get_byte_size_factor("MB")), "M")
    if num_bytes >= _get_byte_size_factor("KB"):
        return (math.ceil(num_bytes / _get_byte_size_factor("KB")), "K")
    return (num_bytes, "B")


@attr.s
class SlurmMem(SlurmRequirement):
    """
    Set memory requirements that specify the maximal amount of memory needed.

    Specify the real memory required per node. Different units can be specified
    using the suffix [K|M|G|T].
    """

    mem_req: int = attr.ib(converter=_to_bytes)

    def to_slurm_cli_opt(self) -> str:
        byte_size_tuple = _to_biggests_byte_size(self.mem_req)
        return f"--mem={byte_size_tuple[0]}{byte_size_tuple[1]}"

    @classmethod
    def merge_requirements(
        cls, lhs_option: 'SlurmMem', rhs_option: 'SlurmMem'
    ) -> 'SlurmMem':
        """
        Merge the requirements of the same type together.
        """
        return copy.deepcopy(max(lhs_option, rhs_option))


def merge_slurm_options(
    list_1: tp.List[Requirement], list_2: tp.List[Requirement]
) -> tp.List[Requirement]:
    """
    Merged two lists of SlurmOptions into one.
    """
    merged_options: tp.Dict[tp.Type[Requirement], Requirement] = dict()

    for opt in list_1 + list_2:
        key = type(opt)
        if key in merged_options:
            current_opt = merged_options[key]
            merged_options[key] = current_opt.merge_requirements(
                current_opt, opt
            )
        else:
            merged_options[key] = opt

    return list(merged_options.values())


def get_slurm_options_from_config() -> tp.List[Requirement]:
    """
    Generates a list of `SlurmOptions` which are specified in the BenchBuild
    config.
    """
    slurm_options: tp.List[Requirement] = []
    if CFG['slurm']['exclusive']:
        slurm_options.append(SlurmExclusive())

    if not CFG['slurm']['multithread']:
        slurm_options.append(SlurmHint({SlurmHint.SlurmHints.nomultithread}))

    slurm_options.append(SlurmTime(str(CFG['slurm']['timelimit'])))
    slurm_options.append(SlurmNiceness(int(CFG['slurm']['nice'])))

    return slurm_options
