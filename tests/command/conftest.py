import pytest
from pytest_git import GitRepo


@pytest.fixture(autouse=True)
def bb_git_repo(git_repo: GitRepo) -> GitRepo:
    path = git_repo.workspace / "bb-test.txt"
    path.write_text("BB Test")

    test = git_repo.workspace / "test"
    test.touch()
    test.chmod("u+x")

    git_repo.api.index.add(path)
    git_repo.api.index.add(test)
    git_repo.api.index.commit("Initial Commit")

    path = git_repo.workspace / "bb-test-2.txt"
    path.write_text("BB Test 2")

    git_repo.api.index.add(path)
    git_repo.api.index.commit("Add BB Test 2")

    return git_repo
