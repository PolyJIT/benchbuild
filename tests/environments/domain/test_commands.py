"""Test command validation & conversion."""
from benchbuild.environments.domain import commands, declarative


def test_image_name_is_lowercase():
    expected = ['test-1', 'test-2']

    cmd_1 = commands.CreateBenchbuildBase(
        'TEST-1', declarative.ContainerImage()
    )
    cmd_2 = commands.CreateImage('TEST-2', declarative.ContainerImage())

    assert [cmd_1.name, cmd_2.name] == expected


def test_containerimage_name_is_lowercase():
    expected = ['test-1', 'containername1']

    cmd_1 = commands.RunProjectContainer('TEST-1', 'ContainerName1', '')

    assert [cmd_1.image, cmd_1.name] == expected
