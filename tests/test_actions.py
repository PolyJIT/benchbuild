"""
Test the actions module.
"""
import unittest

import pytest
from plumbum import ProcessExecutionError

from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.experiment import Experiment
from benchbuild.project import Project
from benchbuild.source import nosource, HTTP
from benchbuild.utils import actions as a


class EmptyProject(Project):
    NAME = "test_empty"
    DOMAIN = "debug"
    GROUP = "debug"
    SOURCE = [nosource()]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def build(self):
        pass

    def configure(self):
        pass

    def download(self):
        pass


class FailAlways(a.Step):
    NAME = "FAIL ALWAYS"
    DESCRIPTION = "A Step that guarantees to fail."

    def __call__(self):
        raise ProcessExecutionError([], 1, "", "")


class PassAlways(a.Step):
    NAME = "PASS ALWAYS"
    DESCRIPTION = "A Step that guarantees to succeed."

    def __call__(self):
        return a.StepResult.OK


class ActionsTestCase(unittest.TestCase):

    def test_for_all_pass(self):
        ep = EmptyProject()
        actn = a.RequireAll(actions=[PassAlways(ep)])
        self.assertEqual(actn(), [a.StepResult.OK])

    def test_for_all_fail(self):
        ep = EmptyProject()
        actn = a.RequireAll(actions=[FailAlways(ep)])
        self.assertEqual(actn(), [a.StepResult.ERROR])


def describe_SetProjectVersion():
    from benchbuild.projects.benchbuild import x264
    from benchbuild.source.base import RevisionStr
    from benchbuild.utils.actions import SetProjectVersion

    class TestExperiment(Experiment):
        NAME = '-'

    class TestProject(Project):
        NAME = '-'
        DOMAIN = '-'
        GROUP = '-'
        SOURCE = [
            HTTP(local='src-a', remote={
                'v1a': '-',
                'v2a': '-',
                'v3': '-'
            }),
            HTTP(local='src-b', remote={
                'v1b': '-',
                'v2b': '-',
                'v3': '-'
            })
        ]

        def compile(self):
            pass

        def run_tests(self):
            pass

    def can_partially_update() -> None:
        exp = TestExperiment(projects=[TestProject])
        context = exp.sample(TestProject)[0]
        prj = TestProject(variant=context)

        assert prj.active_variant['src-a'].version == 'v1a'

        spv = SetProjectVersion(prj, RevisionStr('v2a'))
        with pytest.raises(ProcessExecutionError):
            spv()

        assert prj.active_variant['src-a'].version == 'v2a'

    def can_update_full() -> None:
        exp = TestExperiment(projects=[TestProject])
        context = exp.sample(TestProject)[0]
        prj = TestProject(variant=context)

        assert prj.active_variant['src-a'].version == 'v1a'
        assert prj.active_variant['src-b'].version == 'v1b'

        spv = SetProjectVersion(prj, RevisionStr('v2a'), RevisionStr('v2b'))
        with pytest.raises(ProcessExecutionError):
            spv()

        assert prj.active_variant['src-a'].version == 'v2a'
        assert prj.active_variant['src-b'].version == 'v2b'

    def suffers_from_version_collision() -> None:
        exp = TestExperiment(projects=[TestProject])
        context = exp.sample(TestProject)[0]
        prj = TestProject(variant=context)

        assert prj.active_variant['src-a'].version == 'v1a'
        assert prj.active_variant['src-b'].version == 'v1b'

        spv = SetProjectVersion(prj, RevisionStr('v3'))
        with pytest.raises(ProcessExecutionError):
            spv()

        assert prj.active_variant['src-a'].version == 'v3'
        assert prj.active_variant['src-b'].version == 'v3'
