"""
Orchestrate experiment execution.
"""
import typing as tp

import attr

from benchbuild.experiment import Experiment
from benchbuild.project import Project
from benchbuild.utils import actions, tasks

ExperimentCls = tp.Type[Experiment]
Experiments = tp.List[ExperimentCls]
ProjectCls = tp.Type[Project]
Projects = tp.List[ProjectCls]
ExperimentProject = tp.Tuple[ExperimentCls, ProjectCls]
Actions = tp.Sequence[actions.Step]
StepResults = tp.List[actions.StepResult]


@attr.s
class Experimentator:
    experiments: Experiments = attr.ib()
    projects: Projects = attr.ib()

    _plan: tp.Sequence[actions.Step] = attr.ib(init=False, default=None)

    def plan(self) -> Actions:
        if not self._plan:
            self._plan = tasks.generate_plan(self.experiments, self.projects)

        return self._plan

    @property
    def num_actions(self) -> int:
        p = self.plan()
        return sum([len(child) for child in p])

    def start(self) -> StepResults:
        p = self.plan()
        # Prepare project environment.
        return tasks.execute_plan(p)

    def print_plan(self) -> None:
        p = self.plan()
        print("Number of actions to execute: {}".format(self.num_actions))
        print(*p)
