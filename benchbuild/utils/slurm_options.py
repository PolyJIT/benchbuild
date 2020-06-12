import typing as tp
from enum import Enum
import abc

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
