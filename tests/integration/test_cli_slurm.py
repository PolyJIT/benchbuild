import pytest
from plumbum import local
from rich import print

from benchbuild.cli.slurm import Slurm
from benchbuild.experiment import ExperimentRegistry
from benchbuild.settings import CFG


def test_slurm_command(tmp_path):
    print(CFG['plugins']['experiments'])

    print(ExperimentRegistry.experiments.items())
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with local.cwd(tmp_path):
            Slurm.run(argv=['slurm', '-E', 'empty', 'test'])
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
