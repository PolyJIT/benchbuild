"""
Test the actions module.
"""

import copy
import importlib
import sys
import typing as tp
import unittest

import pytest
from plumbum import ProcessExecutionError

from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.experiment import Experiment
from benchbuild.project import __add_single_filter__, Project
from benchbuild.source import nosource, HTTP
from benchbuild.source.base import RevisionStr
from benchbuild.utils import actions as a
from benchbuild.utils.actions import SetProjectVersion


class EmptyProject(Project):
    NAME = "test_empty"
    DOMAIN = "debug"
    GROUP = "debug"
    SOURCE = [nosource()]
    CONTAINER = ContainerImage().from_("benchbuild:alpine")

    def build(self):
        pass

    def configure(self):
        pass

    def download(self):
        pass


class ExceptAlways(a.ProjectStep):
    NAME = "EXCEPT ALWAYS"
    DESCRIPTION = "A Step that guarantees to fail."

    def __call__(self) -> a.StepResult:
        raise ProcessExecutionError([], 1, "", "")


class FailAlways(a.ProjectStep):
    NAME = "FAIL ALWAYS"
    DESCRIPTION = "A Step that guarantees to fail."

    def __call__(self) -> a.StepResult:
        return a.StepResult.ERROR


class PassAlways(a.ProjectStep):
    NAME = "PASS ALWAYS"
    DESCRIPTION = "A Step that guarantees to succeed."

    def __call__(self) -> a.StepResult:
        return a.StepResult.OK


class ActionsTestCase(unittest.TestCase):
    def test_for_all_pass(self):
        ep = EmptyProject()
        actn = a.RequireAll(actions=[PassAlways(ep)])
        self.assertEqual(actn(), a.StepResult.OK)

    def test_for_all_fail(self):
        ep = EmptyProject()
        actn = a.RequireAll(actions=[FailAlways(ep)])
        self.assertEqual(actn(), a.StepResult.ERROR)

    def test_for_all_except(self):
        ep = EmptyProject()
        actn = a.RequireAll(actions=[ExceptAlways(ep)])
        self.assertEqual(actn(), a.StepResult.ERROR)


class TestProject(Project):
    NAME = "-"
    DOMAIN = "-"
    GROUP = "-"
    SOURCE = [
        HTTP(local="src-a", remote={"v1a": "-", "v2a": "-", "v3": "-"}),
        HTTP(local="src-b", remote={"v1b": "-", "v2b": "-", "v3": "-"}),
    ]

    def compile(self):
        pass

    def run_tests(self):
        pass


@pytest.fixture
def t_project() -> tp.Type[Project]:
    yield TestProject
    importlib.reload(sys.modules[__name__])


class TestExperiment(Experiment):
    NAME = "-"

    def actions_for_project(self, project: Project) -> tp.MutableSequence[a.Step]:
        return []


def test_SetProjectVersion_can_partially_update() -> None:
    exp = TestExperiment(projects=[TestProject])
    context = exp.sample(TestProject)[0]
    prj = TestProject(revision=context)

    assert prj.active_revision.variant_by_name("src-a").version == "v1a"

    spv = SetProjectVersion(prj, RevisionStr("v2a"))
    with pytest.raises(ProcessExecutionError):
        spv()

    assert prj.active_revision.variant_by_name("src-a").version == "v2a"


def test_SetProjectVersion_can_update_full() -> None:
    exp = TestExperiment(projects=[TestProject])
    context = exp.sample(TestProject)[0]
    prj = TestProject(revision=context)

    assert prj.active_revision.variant_by_name("src-a").version == "v1a"
    assert prj.active_revision.variant_by_name("src-b").version == "v1b"

    spv = SetProjectVersion(prj, RevisionStr("v2a"), RevisionStr("v2b"))
    with pytest.raises(ProcessExecutionError):
        spv()

    assert prj.active_revision.variant_by_name("src-a").version == "v2a"
    assert prj.active_revision.variant_by_name("src-b").version == "v2b"


def test_SetProjectVersion_suffers_from_version_collision() -> None:
    exp = TestExperiment(projects=[TestProject])
    context = exp.sample(TestProject)[0]
    prj = TestProject(revision=context)

    assert prj.active_revision.variant_by_name("src-a").version == "v1a"
    assert prj.active_revision.variant_by_name("src-b").version == "v1b"

    spv = SetProjectVersion(prj, RevisionStr("v3"))
    with pytest.raises(ProcessExecutionError):
        spv()

    assert prj.active_revision.variant_by_name("src-a").version == "v3"
    assert prj.active_revision.variant_by_name("src-b").version == "v3"


def test_SetProjectVersion_can_set_revision_through_filter(t_project) -> None:
    """
    Check, if we can set a filtered version.
    """
    source_backup = copy.deepcopy(t_project.SOURCE)

    project_cls = __add_single_filter__(t_project, "v3")
    exp = TestExperiment(projects=[project_cls])
    context = exp.sample(project_cls)[0]
    prj = project_cls(revision=context)

    assert prj.active_revision.variant_by_name("src-a").version == "v3"
    assert prj.active_revision.variant_by_name("src-b").version == "v1b"

    spv = SetProjectVersion(prj, RevisionStr("v1a"))
    with pytest.raises(ProcessExecutionError):
        spv()

    assert prj.active_revision.variant_by_name("src-a").version == "v1a"
    assert prj.active_revision.variant_by_name("src-b").version == "v1b"


def test_SetProjectVersion_raises_error_when_no_revision_is_found() -> None:
    """
    Raise error, if no RevisionStr can be matched with a source.
    """
    exp = TestExperiment(projects=[TestProject])
    context = exp.sample(TestProject)[0]
    prj = TestProject(revision=context)

    assert prj.active_revision.variant_by_name("src-a").version == "v1a"
    assert prj.active_revision.variant_by_name("src-b").version == "v1b"

    with pytest.raises(
        ValueError, match="Revisions (.+) not found in any available source."
    ):
        spv = SetProjectVersion(prj, RevisionStr("does-not-exist"))
