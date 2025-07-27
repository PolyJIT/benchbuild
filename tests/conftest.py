import tempfile as tf
import typing as tp

import faker
import git
import plumbum as pb
import pytest
from faker.providers import file

RepoT = tp.Tuple[pb.local.path, git.Repo]


@pytest.fixture
def mk_git_repo():
    tmp_dir = pb.local.path(tf.mkdtemp())
    fake = faker.Faker()
    fake.add_provider(file)

    def _git_repository(
        num_commits: int = 2, git_submodule: tp.Optional[git.Repo] = None
    ) -> RepoT:
        nonlocal tmp_dir

        a_repo_name = fake.file_name()
        a_repo_base = tmp_dir / a_repo_name
        repo = git.Repo.init(a_repo_base)

        for _ in range(num_commits):
            some_content = fake.text()
            a_name = fake.file_name()
            a_file = a_repo_base / a_name
            with open(a_file, "w") as a_file_handle:
                a_file_handle.writelines(some_content)
            repo.index.add(a_file)
            repo.index.commit(f"Add {a_name}")

        if git_submodule:
            a_sm_path = fake.file_name()
            a_sm_name = fake.file_name()
            repo.create_submodule(
                a_sm_name, a_sm_path, url=git_submodule.git_dir, branch="master"
            )
            repo.index.commit(
                f"Add submodule {a_sm_name} to {a_sm_path} from: {repo.git_dir}"
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
