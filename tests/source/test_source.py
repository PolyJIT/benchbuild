# pylint: disable=redefined-outer-name
import typing as tp
from unittest import mock

import attr
import plumbum as pb
import pytest

from benchbuild import source
from benchbuild.projects.test.test import CAWTestProject, TestProject
from benchbuild.source import FetchableSource, Variant


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

    def versions(self) -> tp.Sequence[Variant]:
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


def test_revision_from_str_can_link_revision_from_single() -> None:
    prj_cls = TestProject
    src = prj_cls.SOURCE[0]
    expected = "test.local"

    select = [source.RevisionStr("1")]
    rev = source.revision_from_str(select, prj_cls)

    assert rev, "No revision has been created."
    assert rev.source_by_name(
        expected
    ).local == src.local, "wrong source in revision."


def test_revision_from_str_can_select_revision_from_multiple() -> None:
    prj_cls = CAWTestProject
    src = prj_cls.SOURCE[0]
    expected = "test.local"

    # explore() is currently not supported by CAW sources
    select = [source.RevisionStr("caw_0")]

    with pytest.raises(ValueError):
        rev = source.revision_from_str(select, prj_cls)

    select = [source.RevisionStr("4")]

    with pytest.raises(ValueError):
        rev = source.revision_from_str(select, prj_cls)
        rev.source_by_name(expected)

    select = [source.RevisionStr("2")]
    rev = source.revision_from_str(select, prj_cls)

    assert rev.source_by_name(expected) == src, "source not in this revision."


def test_revision_from_str_finds_all_requested_revisions(src_a, src_b) -> None:
    prj_cls = CAWTestProject
    select = [source.RevisionStr("1"), source.RevisionStr("2")]
    src = prj_cls.SOURCE[0]
    caw_src = prj_cls.SOURCE[1]
    expected = "test.local"
    not_expected = "test.caw.local"

    rev = source.revision_from_str(select, TestProject)

    assert rev, "No context has been created."

    assert rev.source_by_name(
        expected
    ).local == src.local, "src not in context."

    with pytest.raises(KeyError):
        assert rev.source_by_name(
            not_expected
        ) == caw_src, "caw_src not in context."


#def test_base_context(src_a):
#    var = src_a.default
#    ctx = source.context(var)
#
#    assert ctx[src_a.local].owner == src_a
#    assert ctx[src_a.local] == var
#
#    with pytest.raises(KeyError):
#        ctx['non-existing']  # pylint: disable=pointless-statement


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


def test_explore_with_filter(make_source):
    """
    Make sure we can access revisions that would have been filtered.

    Source.explore should not filter anything.
    """
    src_1 = make_source(range(2))

    src = source.SingleVersionFilter(src_1, '0')
    src_vs = [str(v) for v in src.versions()]
    src_explore = [str(v) for v in src.explore()]

    assert ['0'] == src_vs
    assert ['0', '1'] == src_explore


def test_git_submodule_versions_do_not_get_expanded():
    git_repo = source.Git('remote.git', 'local.git', clone=False)
    git_repo.versions = mock.MagicMock(name='versions')
    git_repo.versions.return_value = ['1', '2', '3']

    git_repo_sub = source.GitSubmodule(
        'remote.sub.git', 'local.git/sub', clone=False
    )
    git_repo_sub.versions = mock.MagicMock(name='versions')
    git_repo_sub.versions.return_value = ['sub1', 'sub2', 'sub3']

    variants = list(source.product(git_repo, git_repo_sub))
    expected_variants = [('1',), ('2',), ('3',)]

    assert variants == expected_variants


@mock.patch('benchbuild.source.git.base.target_prefix')
def test_git_repo_can_be_fetched(mocked_prefix, simple_repo):
    base_dir, repo = simple_repo
    mocked_prefix.return_value = str(base_dir)

    a_repo = source.Git(remote=repo.git_dir, local='test.git')
    cache_path = a_repo.fetch()

    assert (base_dir / 'test.git').exists()
    assert cache_path == str(base_dir / 'test.git')


@mock.patch('benchbuild.source.git.base.target_prefix')
def test_git_repo_clones_submodules(mocked_prefix, repo_with_submodule):
    base_dir, repo = repo_with_submodule
    mocked_prefix.return_value = str(base_dir)

    a_repo = source.Git(remote=repo.git_dir, local='test.git')
    a_repo.fetch()

    for submodule in repo.submodules:
        expected_sm_path = base_dir / 'test.git' / submodule.path
        assert expected_sm_path.exists()
        assert expected_sm_path.list() != []


@mock.patch('benchbuild.source.git.base.target_prefix')
def test_git_submodule_can_be_fetched_outside_main(
    mocked_prefix, repo_with_submodule
):
    base_dir, repo = repo_with_submodule
    mocked_prefix.return_value = str(base_dir)

    a_repo = source.Git(remote=repo.git_dir, local='test.git')
    a_repo.fetch()

    for submodule in repo.submodules:
        expected_sub_path_outside = base_dir / 'outside_main.git'
        expected_sub_path_inside = base_dir / 'test.git' / submodule.path

        a_sub_repo = source.GitSubmodule(
            remote=submodule.url, local='outside_main.git'
        )
        a_sub_repo.fetch()

        assert expected_sub_path_outside.exists()
        assert expected_sub_path_outside.list() != []

        assert expected_sub_path_inside.exists()
        assert expected_sub_path_inside.list() != []


@mock.patch('benchbuild.source.git.base.target_prefix')
def test_git_submodule_can_be_fetched_inside_fetched_main(
    mocked_prefix, repo_with_submodule
):
    base_dir, repo = repo_with_submodule
    mocked_prefix.return_value = str(base_dir)

    a_repo = source.Git(remote=repo.git_dir, local='test.git')
    a_repo.fetch()

    for submodule in repo.submodules:
        expected_sub_path = base_dir / 'test.git' / submodule.path
        expected_flat_sub_path = base_dir / f'test.git-{submodule.path}'

        sub_path = f'test.git/{submodule.path}'
        a_sub_repo = source.GitSubmodule(
            remote=submodule.url, local=str(sub_path)
        )
        cache_patch = a_sub_repo.fetch()

        assert expected_sub_path.exists()
        assert expected_flat_sub_path.exists()
        assert expected_sub_path.list() != []
        assert expected_flat_sub_path.list() != []
        assert cache_patch == expected_flat_sub_path


@mock.patch('benchbuild.source.git.base.target_prefix')
def test_git_repo_can_list_versions(mocked_prefix, simple_repo):
    base_dir, repo = simple_repo
    mocked_prefix.return_value = str(base_dir)
    master = repo.head.reference

    a_repo = source.Git(remote=repo.git_dir, local='test.git')
    expected_versions = [v.newhexsha[0:a_repo.limit] for v in master.log()]
    found_versions = [str(v) for v in reversed(a_repo.versions())]

    assert expected_versions == found_versions
