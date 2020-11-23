# pylint: disable=redefined-outer-name
import tempfile as tf
import typing as tp
from unittest import mock

import attr
import git
import plumbum as pb
import pytest
import testdata as td

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


RepoT = tp.Tuple[pb.local.path, git.Repo]


@pytest.fixture
def mk_git_repo():
    tmp_dir = pb.local.path(tf.mkdtemp())

    def _git_repository(
        num_commits: int = 2,
        git_submodule: tp.Optional[git.Repo] = None
    ) -> RepoT:
        nonlocal tmp_dir

        a_repo_name = td.get_file_name()
        a_repo_base = tmp_dir / a_repo_name
        repo = git.Repo.init(a_repo_base)

        for _ in range(num_commits):
            some_content = td.get_str(255)
            a_name = td.get_file_name()
            a_file = td.create_file(
                a_name, contents=some_content, tmpdir=a_repo_base
            )
            repo.index.add(a_file)
            repo.index.commit(f'Add {a_name}')

        if git_submodule:
            a_sm_path = td.get_file_name()
            a_sm_name = td.get_file_name()
            repo.create_submodule(
                a_sm_name,
                a_sm_path,
                url=git_submodule.git_dir,
                branch='master'
            )
            repo.index.commit(
                f'Add submodule {a_sm_name} to {a_sm_path} from: {repo.git_dir}'
            )

            return (tmp_dir, repo)
        return (tmp_dir, repo)

    yield _git_repository
    tmp_dir.delete()


@pytest.fixture
def simple_repo(mk_git_repo) -> RepoT:
    yield mk_git_repo()


@pytest.fixture
def repo_with_submodule(mk_git_repo) -> RepoT:
    base_dir, sub_repo = mk_git_repo()
    _, main_repo = mk_git_repo(git_submodule=sub_repo)

    yield (base_dir, main_repo)


def describe_git():

    def submodule_versions_do_not_get_expanded():
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
    def repo_can_be_fetched(mocked_prefix, simple_repo):
        base_dir, repo = simple_repo
        mocked_prefix.return_value = str(base_dir)

        a_repo = source.Git(remote=repo.git_dir, local='test.git')
        cache_path = a_repo.fetch()

        assert (base_dir / 'test.git').exists()
        assert cache_path == str(base_dir / 'test.git')

    @mock.patch('benchbuild.source.git.base.target_prefix')
    def repo_clones_submodules(mocked_prefix, repo_with_submodule):
        base_dir, repo = repo_with_submodule
        mocked_prefix.return_value = str(base_dir)

        a_repo = source.Git(remote=repo.git_dir, local='test.git')
        a_repo.fetch()

        for submodule in repo.submodules:
            expected_sm_path = base_dir / 'test.git' / submodule.path
            assert expected_sm_path.exists()
            assert expected_sm_path.list() != []

    @mock.patch('benchbuild.source.git.base.target_prefix')
    def submodule_can_be_fetched_outside_main(
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
    def submodule_can_be_fetched_inside_fetched_main(
        mocked_prefix, repo_with_submodule
    ):
        base_dir, repo = repo_with_submodule
        mocked_prefix.return_value = str(base_dir)

        a_repo = source.Git(remote=repo.git_dir, local='test.git')
        a_repo.fetch()

        for submodule in repo.submodules:
            expected_sub_path = base_dir / 'test.git' / submodule.path
            sub_path = f'test.git/{submodule.path}'
            a_sub_repo = source.GitSubmodule(
                remote=submodule.url, local=str(sub_path)
            )
            a_sub_repo.fetch()

            assert expected_sub_path.exists()
            assert expected_sub_path.list() != []

    @mock.patch('benchbuild.source.git.base.target_prefix')
    def repo_can_list_versions(mocked_prefix, simple_repo):
        base_dir, repo = simple_repo
        mocked_prefix.return_value = str(base_dir)
        master = repo.head.reference

        a_repo = source.Git(remote=repo.git_dir, local='test.git')
        expected_versions = [v.newhexsha[0:a_repo.limit] for v in master.log()]
        found_versions = [str(v) for v in reversed(a_repo.versions())]

        assert expected_versions == found_versions
