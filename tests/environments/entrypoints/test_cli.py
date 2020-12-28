"""
Test declarative API
"""
from benchbuild.environments.entrypoints import cli
from benchbuild.experiments.empty import Empty
from tests.project.test_project import DummyPrj, DummyPrjNoContainerImage


def test_cli_enumerates_only_supported_projects():
    prj_index = {
        'TestPrj/TestGrp': DummyPrj,
        'TestPrjNoContainer/TestGrp': DummyPrjNoContainerImage
    }
    exp_index = {'empty': Empty}
    prjs = list(cli.enumerate_projects(exp_index, prj_index))

    assert len(prjs) == 1
