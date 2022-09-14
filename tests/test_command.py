from pathlib import Path, PosixPath

from benchbuild.command import (
    Command,
    ProjectCommand,
    PathToken,
    RootRenderer,
    enable_rollback,
)
from benchbuild.projects.test import TestProject

TT = PathToken.make_token(RootRenderer())


def test_basic_command():
    cmd = Command(TT / "bin" / "true")
    assert cmd.dirname == PosixPath("/bin")
    assert cmd.name == "true"

    cmd_path = cmd.path.render()
    assert cmd_path.exists()


def test_basic_command_exists():
    cmd = Command(TT / ".benchbuild_true_does_not_exist")

    cmd_path = cmd.path.render()
    assert not cmd_path.exists()


def test_basic_command_args():
    expected_str = "Command(path=/ignore args=('1', '2', 'three'))"
    cmd = Command(TT / "ignore", 1, "2", "three")
    assert repr(cmd) == expected_str

    cmd = Command(TT / "ignore")
    cmd = cmd[1, "2", "three"]
    assert repr(cmd) == expected_str


def test_basic_command_env():
    expected_str = "Command(path=/ignore env={'E1': 1, 'E2': '2', 'E3': 'three'})"
    cmd = Command(TT / "ignore", E1=1, E2="2", E3="three")
    assert repr(cmd) == expected_str


def test_as_plumbum():
    expected_str = "/bin/true"
    cmd = Command(TT / "/bin/true")
    assert str(cmd.as_plumbum()) == expected_str

    expected_str = "/bin/true 1 2 three"
    pb_cmd = cmd[1, "2", "three"].as_plumbum()
    assert str(pb_cmd) == expected_str


def test_rollback_creates(tmp_path):
    expected_path = tmp_path / "bar"
    cmd = Command(
        TT / "usr" / "bin" / "touch",
        expected_path,
        creates=[TT / str(tmp_path)]
    )
    p_cmd = ProjectCommand(TestProject, cmd)

    assert not expected_path.exists()
    p_cmd()
    assert expected_path.exists()

    with enable_rollback(p_cmd):
        p_cmd()
    assert not expected_path.exists()


def test_rollback_creates(tmp_path):
    expected_path = tmp_path / "bar"
    touch_cmd = Command(
        TT / "usr" / "bin" / "touch",
        expected_path,
        creates=[TT / str(tmp_path)]
    )

    rm_cmd = Command(
        TT / "usr" / "bin" / "rm", expected_path, consumes=[TT / str(tmp_path)]
    )

    assert not expected_path.exists()
    touch_cmd()
    assert expected_path.exists()

    with enable_rollback(ProjectCommand(TestProject(), rm_cmd)):
        rm_cmd()

    assert expected_path.exists()
