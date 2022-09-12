import pytest
from pytest_git import GitRepo

import benchbuild.command as c
from benchbuild.command import WorkloadSet, OnlyIn, Command, SourceRoot
from benchbuild.experiments.empty import NoMeasurement
from benchbuild.project import Project, ProjectT
from benchbuild.source.git import Git
from benchbuild.utils.actions import RunWorkloads, StepResult
from benchbuild.utils.revision_ranges import RevisionRange
from benchbuild.utils.tasks import generate_plan, execute_plan


class DefaultWorkloadProject(Project):
    NAME = "workload-test"
    DOMAIN = "tests"
    GROUP = "tests"

    SOURCE = []
    WORKLOADS = {WorkloadSet("always"): [Command(SourceRoot() / "true")]}

    def compile(self) -> None:
        pass

    def run_tests(self) -> None:
        pass


class OnlyInWorkloadProject(Project):
    NAME = "workload-test"
    DOMAIN = "tests"
    GROUP = "tests"

    SOURCE = []
    WORKLOADS = {
        OnlyIn(RevisionRange("HEAD~1", "HEAD"), WorkloadSet("sometimes")): [
            Command(SourceRoot() / "true")
        ],
        WorkloadSet("always"): [Command(SourceRoot() / "true")]
    }

    def compile(self) -> None:
        pass

    def run_tests(self) -> None:
        pass


@pytest.fixture
def project(bb_git_repo: GitRepo) -> ProjectT:
    DefaultWorkloadProject.SOURCE = [
        Git(
            remote=bb_git_repo.workspace,
            local="workload-test.git",
            shallow=False
        )
    ]
    return DefaultWorkloadProject


@pytest.fixture
def only_in_project(bb_git_repo: GitRepo) -> ProjectT:
    OnlyInWorkloadProject.SOURCE = [
        Git(
            remote=bb_git_repo.workspace,
            local="workload-test.git",
            shallow=False
        )
    ]
    return OnlyInWorkloadProject


def test_workload_can_unwrap(project: ProjectT, only_in_project: ProjectT):
    p = project()
    op = only_in_project = only_in_project()

    workloads = c.unwrap(p.workloads, p)
    assert all(isinstance(w, WorkloadSet) for w in workloads)

    workloads = c.unwrap(op.workloads, op)
    assert all(isinstance(w, WorkloadSet) for w in workloads)


def test_workload_run(project: ProjectT):
    plan = generate_plan([NoMeasurement], [project])
    res = execute_plan(plan)

    assert res == [StepResult.OK]
