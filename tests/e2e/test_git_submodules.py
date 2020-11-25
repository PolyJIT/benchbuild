import typing as tp

import pytest

import benchbuild as bb
from benchbuild import source, engine
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.extensions.base import Extension
from benchbuild.settings import CFG
from benchbuild.source import Git, GitSubmodule
from benchbuild.utils import run, log

log.configure()
log.set_defaults()


class NoopExtension(Extension):

    def __call__(self, *args, **kwargs) -> tp.List[run.RunInfo]:
        return [run.RunInfo()]


class ExperimentTest(bb.Experiment):
    NAME = 'test-experiment'
    CONTAINER = ContainerImage()

    def actions_for_project(self, project):
        project.compiler_extension = NoopExtension()
        project.runtime_extension = NoopExtension()
        return self.default_runtime_actions(project)


class GitSubmoduleTestProject(bb.Project):
    """
    E2E Test for GitSubmodule
    """
    NAME = 'test-git-submodule'
    DOMAIN = 'tests'
    GROUP = 'tests'
    SOURCE = []
    CONTAINER = ContainerImage()

    def run_tests(self):
        pass

    def compile(self):
        pass


@pytest.fixture
def project_cls(repo_with_submodule):
    base_dir, repo = repo_with_submodule

    build_dir = str(CFG['build_dir'])
    tmp_dir = str(CFG['tmp_dir'])

    CFG['build_dir'] = str(base_dir)
    CFG['tmp_dir'] = str(base_dir)

    GitSubmoduleTestProject.SOURCE = [
        Git(remote=repo.git_dir, local='test.git'),
        GitSubmodule(remote=repo.submodules[0].url, local='test.git/sub.git')
    ]
    yield GitSubmoduleTestProject

    CFG['build_dir'] = build_dir
    CFG['tmp_dir'] = tmp_dir


def test_project_creates_variants(project_cls):
    assert len(list(source.product(*project_cls.SOURCE))) > 0


def test_project_environment_with_submodules(project_cls):
    ngn = engine.Experimentator(
        experiments=[ExperimentTest], projects=[project_cls]
    )

    failed = ngn.start()

    assert len(failed) == 0
