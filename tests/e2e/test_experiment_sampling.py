import typing as tp

import mock
import plumbum as pb
import pytest

import benchbuild as bb
from benchbuild import source, engine
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.extensions.base import Extension
from benchbuild.settings import CFG
from benchbuild.source import Git, GitSubmodule
from benchbuild.utils import run, log, slurm
from tests import conftest as ct

log.configure()
log.set_defaults()

NUM_COMMITS = 10
EXPECTED_COMMITS = 5


class NoopExtension(Extension):

    def __call__(self, *args, **kwargs) -> tp.List[run.RunInfo]:
        return [run.RunInfo()]


class SampleExperiment(bb.Experiment):
    NAME = 'test-experiment-sampling'
    CONTAINER = ContainerImage()

    def actions_for_project(self, project):
        project.compiler_extension = NoopExtension()
        project.runtime_extension = NoopExtension()
        return self.default_runtime_actions(project)

    @classmethod
    def sample(cls,
               prj_cls: bb.project.ProjectT) -> tp.Sequence[source.Revision]:
        return source.enumerate_revisions(prj_cls)[:EXPECTED_COMMITS]


class SampleProject(bb.Project):
    """
    E2E Test project for experiment version sampling.
    """
    NAME = 'test-experiment-sampling'
    DOMAIN = 'tests'
    GROUP = 'tests'
    SOURCE = []
    CONTAINER = ContainerImage()

    def run_tests(self):
        pass

    def compile(self):
        pass


@pytest.fixture
def repo_with_submodule(mk_git_repo) -> ct.RepoT:
    """Override toplevel fixture with a larger default repo."""
    base_dir, sub_repo = mk_git_repo(num_commits=NUM_COMMITS)
    _, main_repo = mk_git_repo(num_commits=NUM_COMMITS, git_submodule=sub_repo)

    yield (base_dir, main_repo)


@pytest.fixture
def project_cls(repo_with_submodule):
    base_dir, repo = repo_with_submodule

    build_dir = str(CFG['build_dir'])
    tmp_dir = str(CFG['tmp_dir'])

    CFG['build_dir'] = str(base_dir)
    CFG['tmp_dir'] = str(base_dir)

    SampleProject.SOURCE = [
        Git(remote=repo.git_dir, local='test.git'),
        GitSubmodule(remote=repo.submodules[0].url, local='test.git/sub.git')
    ]
    yield SampleProject

    CFG['build_dir'] = build_dir
    CFG['tmp_dir'] = tmp_dir


def test_experiment_can_sample(project_cls):
    contexts = SampleExperiment.sample(project_cls)
    assert len(contexts) == EXPECTED_COMMITS


@mock.patch('tests.e2e.test_experiment_sampling.SampleExperiment.sample')
def test_sampling_is_used_by_benchbuild_run(mocked_sample, project_cls):
    """
    Check, if a generated plan has used the experiment's sample method.

    This is the path used by 'benchbuild run'
    """
    ngn = engine.Experimentator(
        experiments=[SampleExperiment], projects=[project_cls]
    )

    num_actions = ngn.num_actions
    assert num_actions > 0

    mocked_sample.assert_called_with(project_cls)


@mock.patch('tests.e2e.test_experiment_sampling.SampleExperiment.sample')
def test_sampling_is_used_by_benchbuild_slurm(
    mocked_sample, tmp_path, project_cls
):
    """
    Check, if a generated plan has used the experiment's sample method.

    This is the path used by 'benchbuild slurm'
    """
    exp = SampleExperiment(projects=[project_cls])

    with pb.local.cwd(str(tmp_path)):
        slurm.script(exp, 'run')

    mocked_sample.assert_called_with(project_cls)
