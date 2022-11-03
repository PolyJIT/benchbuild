# pylint: disable=redefined-outer-name
import typing as tp

import attr
import pytest
import yaml
from plumbum import local

from benchbuild import Project
from benchbuild.environments.domain import declarative
from benchbuild.project import (
    discovered,
    __add_filters__,
    __add_indexed_filters__,
    __add_named_filters__,
    __add_single_filter__,
)
from benchbuild.source import (
    FetchableSource,
    SingleVersionFilter,
    Variant,
    nosource,
    primary,
)


class DummyPrj(Project):
    NAME = 'TestPrj'
    DOMAIN = 'TestDom'
    GROUP = 'TestGrp'
    SOURCE = [nosource()]
    CONTAINER = declarative.ContainerImage().from_('benchbuild:alpine')

    def run_tests(self):
        raise NotImplementedError()


class DummyPrjEmptySource(Project):
    NAME = 'TestPrj'
    DOMAIN = 'TestDom'
    GROUP = 'TestGrp'
    SOURCE = []
    CONTAINER = declarative.ContainerImage().from_('benchbuild:alpine')

    def run_tests(self):
        raise NotImplementedError()


class DummyPrjNoContainerImage(Project):
    NAME = 'TestPrjNoContainer'
    DOMAIN = 'TestDom'
    GROUP = 'TestGrp'
    SOURCE = [nosource()]

    def run_tests(self):
        raise NotImplementedError()


@pytest.fixture(params=[['1'], ['1', '2']], ids=['single', 'multi'])
def mksource(request) -> tp.Callable[[str], FetchableSource]:

    class VersionSource(FetchableSource):
        test_versions: tp.List[str]

        def __init__(
            self, local: str, remote: tp.Union[str, tp.Dict[str, str]],
            test_versions: tp.List[str]
        ):
            super().__init__(local, remote)

            self.test_versions = test_versions

        @property
        def default(self):
            return self.versions()[0]

        def version(self, target_dir, version):
            return version

        def versions(self):
            return [Variant(self, version) for version in self.test_versions]

    def source_factory(name: str = 'VersionSource') -> FetchableSource:
        cls = type(name, (VersionSource,), {})
        return cls(local=name, remote='', test_versions=request.param)

    return source_factory


@pytest.fixture
def mkproject(mksource):

    def project_factory(name: str = 'VersionedProject', num_sources: int = 1):

        class VersionedProject(Project):
            NAME = DOMAIN = GROUP = name
            SOURCE = [
                mksource(f'VersionSource_{i}') for i in range(num_sources)
            ]
            CONTAINER = declarative.ContainerImage().from_('benchbuild:alpine')

        return VersionedProject

    return project_factory


@attr.s
class TI:
    t_filter = attr.ib()
    t_input = attr.ib()
    t_input_not_in = attr.ib()
    t_expect = attr.ib()


@pytest.fixture(
    params=[
        TI(__add_single_filter__, "1", "ni", '1'),
        TI(__add_indexed_filters__, ["1"], ["ni"], '1'),
        TI(
            __add_named_filters__, {"VersionSource_0": "1"},
            {"VersionSource_0": "ni"}, '1'
        ),
    ],
    ids=['single-1', 'indexed-1', 'named-1']
)
def filter_test(request):
    return request.param


@pytest.fixture(
    params=[('SingleSource', 1), ('MultiSource', 2)],
    ids=['SingleSource', 'MultiSource']
)
def project(mkproject, request):
    name, num = request.param
    return mkproject(name, num)


@pytest.fixture
def project_instance(project):
    return project()


def test_project_has_version_of(project_instance):
    assert hasattr(project_instance, 'version_of_primary')


def test_project_has_source_of(project_instance):
    assert hasattr(project_instance, 'source_of_primary')


def test_project_has_version_of_primary(project_instance):
    assert project_instance.version_of_primary == '1'


def test_project_has_source_of_primary(project_instance):
    assert local.path(
        project_instance.source_of_primary
    ).name == 'VersionSource_0'


def test_project_source_must_contain_elements():
    with pytest.raises(ValueError) as excinfo:
        DummyPrjEmptySource()
    assert "A project requires at least one source!" in str(excinfo)


def test_filters_is_generated_by_add_filters(project, filter_test):  # pylint: disable=unused-variable
    filtered_prj = __add_filters__(project, str(filter_test.t_input))
    assert isinstance(primary(*filtered_prj.SOURCE), SingleVersionFilter)


def test_filters_wraps_primary(project, filter_test):  # pylint: disable=unused-variable
    filtered = filter_test.t_filter(project, filter_test.t_input)
    filtered_source = primary(*filtered.SOURCE)
    assert isinstance(filtered_source, SingleVersionFilter)


def test_filters_returns_no_versions_if_unmatched(project, filter_test):  # pylint: disable=unused-variable
    filtered = filter_test.t_filter(project, filter_test.t_input_not_in)
    filtered_source = primary(*filtered.SOURCE)

    assert len(filtered_source.versions()) == 0


def test_filters_matches_return_only_one_version(project, filter_test):  # pylint: disable=unused-variable
    filtered = filter_test.t_filter(project, filter_test.t_input)
    filtered_source = primary(*filtered.SOURCE)

    assert len(filtered_source.versions()) == 1
    var_1 = Variant(None, filter_test.t_expect)
    assert all([v == var_1 for v in filtered_source.versions()])


def test_filters_named_unchanged_if_unmatched(project):  # pylint: disable=unused-variable
    um_filter = {'not-in': '1'}
    filtered = __add_named_filters__(project, um_filter)

    for src in filtered.SOURCE:
        assert not isinstance(src, SingleVersionFilter)


@pytest.fixture(scope='class', params=discovered().values())
def prj_cls(request):
    return request.param


def test_default_projects_containerimage_is_optional_on_subclass(prj_cls):
    if not hasattr(prj_cls, 'CONTAINER'):
        prj = prj_cls()
        assert prj.container is not None
