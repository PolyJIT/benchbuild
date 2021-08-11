import typing as tp

import pytest
from plumbum import local

from benchbuild.cli.slurm import Slurm
from benchbuild.utils import cmd


@pytest.fixture
def cmd_mock() -> tp.Callable[[str], None]:

    def _cmd_mock(name: str):
        cmd.__overrides__[name] = ['/bin/true']

    yield _cmd_mock
    cmd.__overrides__ = {}


def test_slurm_command(tmp_path, cmd_mock):
    cmd_mock('srun')

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with local.cwd(tmp_path):
            Slurm.run(argv=['slurm', '-E', 'empty', 'test'])
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
