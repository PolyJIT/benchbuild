# pylint: disable=redefined-outer-name
import attr
import pytest
from plumbum import local

from benchbuild import Project
from benchbuild.source import nosource


class DummyPrj(Project):
    NAME = 'TestPrj'
    DOMAIN = 'TestDom'
    GROUP = 'TestGrp'
    SOURCE = [nosource()]

    def run_tests(self):
        raise NotImplementedError()


class DummyPrjEmptySource(Project):
    NAME = 'TestPrj'
    DOMAIN = 'TestDom'
    GROUP = 'TestGrp'
    SOURCE = []

    def run_tests(self):
        raise NotImplementedError()


@pytest.fixture
def dummy_exp():
    return attr.make_class('TestExp', {'name': attr.ib(default='TestExp')})


def test_attr_version_of(dummy_exp):
    prj = DummyPrj(experiment=dummy_exp())
    assert hasattr(prj, 'version_of_primary')


def test_attr_source_of(dummy_exp):
    prj = DummyPrj(experiment=dummy_exp())
    assert hasattr(prj, 'source_of_primary')


def test_version_of_primary(dummy_exp):
    prj = DummyPrj(experiment=dummy_exp())
    assert prj.version_of_primary == 'None'


def test_source_of_primary(dummy_exp):
    prj = DummyPrj(experiment=dummy_exp())
    assert local.path(prj.source_of_primary).name == 'NoSource'


def test_primary_source(dummy_exp):
    with pytest.raises(TypeError) as excinfo:
        DummyPrjEmptySource(experiment=dummy_exp())
    assert "primary()" in str(excinfo)
