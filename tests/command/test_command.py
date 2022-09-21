from pathlib import Path, PosixPath

from benchbuild.command import (
    Command,
    ProjectCommand,
    PathToken,
    RootRenderer,
    cleanup,
)
from benchbuild.projects.test.test import TestProject

TT = PathToken.make_token(RootRenderer())


def test_basic_command():
    cmd = Command(TT / "bin" / "true")
    assert cmd.dirname == PosixPath("/bin")
    assert cmd.name == "true"

    cmd_path = cmd.path.render()
    assert cmd_path.exists()


def test_command_label():
    my_label = "MyLabel"
    other_label = "OtherLabel"
    cmd: Command = Command(TT / "bin" / "true", label=my_label)

    assert cmd.label == my_label

    cmd.label = other_label

    assert cmd.label == other_label


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
    cmd = Command(TT / "bin" / "false", creates=[TT / str(expected_path)])
    prj = TestProject()
    prj.builddir = tmp_path

    p_cmd = ProjectCommand(prj, cmd)
    with cleanup(p_cmd):
        expected_path.touch()
        assert expected_path.exists()
    assert not expected_path.exists()


def test_rollback_consumes(tmp_path):
    expected_path = tmp_path / "bar"
    cmd = Command(TT / "bin" / "false", consumes=[TT / str(expected_path)])

    prj = TestProject()
    prj.builddir = tmp_path

    p_cmd = ProjectCommand(prj, cmd)

    expected_path.touch()
    with cleanup(p_cmd):
        assert expected_path.exists()
        expected_path.unlink()
        assert not expected_path.exists()
    assert expected_path.exists()
