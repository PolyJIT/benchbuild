# pylint: disable=redefined-outer-name
import typing as tp

import attr
import plumbum as pb
import pytest

from benchbuild import source
from benchbuild.source import FetchableSource, Variant

Variants = tp.Iterable[Variant]


class SimpleSource(FetchableSource):
    test_versions: tp.List[str] = attr.ib()

    def __init__(
        self, local: str, remote: tp.Union[str, tp.Dict[str, str]],
        test_versions: tp.List[str]
    ):
        super().__init__(local, remote)

        self.test_versions = test_versions

    @property
    def default(self) -> Variant:
        return Variant(owner=self, version=self.test_versions[0])

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        return pb.local.path('.') / f'bb-test-{version}'

    def versions(self) -> Variants:
        return [Variant(self, v) for v in self.test_versions]


@pytest.fixture
def versions_a():
    return ["1.0a", "2.0a"]


@pytest.fixture
def versions_b():
    return ["1.0b", "2.0b"]


@pytest.fixture
def src_a(versions_a):
    return SimpleSource(
        local='src_A_local', remote='src_A_remote', test_versions=versions_a
    )


@pytest.fixture
def src_b(versions_b):
    return SimpleSource(
        local='src_B_local', remote='src_B_remote', test_versions=versions_b
    )


def test_base_context(src_a):
    var = src_a.default
    ctx = source.context(var)

    assert ctx[src_a.local].owner == src_a
    assert ctx[src_a.local] == var

    with pytest.raises(KeyError):
        ctx['non-existing']  # pylint: disable=pointless-statement


def test_base_to_str(src_a, src_b, versions_a, versions_b):
    vars_a = src_a.versions()
    vars_b = src_b.versions()

    version_text = source.to_str(*vars_a)
    assert version_text == ",".join(versions_a)
    version_text = source.to_str(*vars_b)
    assert version_text == ",".join(versions_b)

    vars_ab = versions_a + versions_b
    version_text = source.to_str(*vars_a, *vars_b)
    assert version_text == ",".join(vars_ab)


def test_base_default(src_a, src_b):
    default_versions = source.default(src_a, src_b)

    assert src_a.local in default_versions
    assert default_versions[src_a.local] == src_a.default
    assert src_b.local in default_versions
    assert default_versions[src_b.local] == src_b.default


def test_base_product(src_a, src_b):
    all_versions = list(source.product(src_a, src_b))
    assert all([len(v) == 2 for v in all_versions])
    assert len(all_versions) == len(src_a.versions()) * len(src_b.versions())


def test_git_clone_needed():
    pass


def test_git_maybe_shallow():
    pass


def test_http_normalize_remote():
    pass


def test_http_versioned_target_name():
    pass


def test_http_download_single_version():
    pass


def test_http_download_required():
    pass


class VersionSource(FetchableSource):
    known_versions: tp.List[str]

    def __init__(
        self, local: str, remote: tp.Union[str, tp.Dict[str, str]],
        known_versions: tp.List[str]
    ):
        super().__init__(local, remote)

        self.known_versions = known_versions

    @property
    def default(self) -> Variant:
        return Variant(owner=self, version='1')

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        return '.'

    def versions(self) -> tp.List[Variant]:
        return [Variant(self, str(v)) for v in self.known_versions]


@pytest.fixture
def make_source():

    def _make_version_source(versions: tp.List[int]):
        str_versions = [str(v) for v in versions]
        return VersionSource('ls', 'rs', str_versions)

    return _make_version_source


def test_single_versions_filter(make_source):
    src_1 = make_source([0])
    src_2 = make_source(range(2))

    src = source.SingleVersionFilter(src_1, '0')
    src_vs = [str(v) for v in src.versions()]
    assert ['0'] == src_vs

    src = source.SingleVersionFilter(src_2, '-1')
    src_vs = [str(v) for v in src.versions()]
    assert [] == src_vs

    src = source.SingleVersionFilter(src_2, '1')
    src_vs = [str(v) for v in src.versions()]
    assert ['1'] == src_vs

    src = source.SingleVersionFilter(src_2, '2')
    src_vs = [str(v) for v in src.versions()]
    assert [] == src_vs


def test_versions_product():
    pass
