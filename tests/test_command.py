from pathlib import Path, PosixPath

from benchbuild.command import Command, ProjectCommand
from benchbuild.project import Project

from .project import test_project as tp


def test_basic_command():
    cmd = Command(Path("/bin/true"))
    assert cmd.dirname == PosixPath("/bin")
    assert cmd.name == "true"
    assert cmd.exists()


def test_basic_command_exists():
    cmd = Command(Path("/.benchbuild_true_does_not_exist"))
    assert not cmd.exists()


def test_basic_command_args():
    expected_str = "Command(path=ignore args=(1, '2', 'three'))"
    cmd = Command(Path("ignore"), 1, "2", "three")
    assert repr(cmd) == expected_str

    cmd = Command(Path("ignore"))
    cmd = cmd[1, "2", "three"]
    assert repr(cmd) == expected_str


def test_basic_command_env():
    expected_str = "Command(path=ignore env={'E1': 1, 'E2': '2', 'E3': 'three'})"
    cmd = Command(Path("ignore"), E1=1, E2="2", E3="three")
    assert repr(cmd) == expected_str
