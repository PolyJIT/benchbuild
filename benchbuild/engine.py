"""
Orchestrate experiment execution.
"""
from typing import Callable, List, Tuple, Type

import attr
from benchbuild.experiment import Experiment
from benchbuild.project import Project
from benchbuild.utils import actions, tasks

ExperimentCls = Type[Experiment]
Experiments = Type[List[ExperimentCls]]
ProjectCls = Type[Project]
Projects = Type[List[ProjectCls]]
ExperimentProject = Tuple[ExperimentCls, ProjectCls]
ExpStrategy: Type = Type[Callable[[List[Experiment], List[Project]], List[
    Tuple[Experiment, Project]]]]


@attr.s
class Experimentator:
    experiments: List[Experiment] = attr.ib()
    projects: List[Project] = attr.ib()

    _plan: List[actions.Step] = attr.ib(init=False, default=None)

    def plan(self):
        if not self._plan:
            self._plan = tasks.generate_plan(self.experiments, self.projects)

        return self._plan

    @property
    def num_actions(self):
        p = self.plan()
        return sum([len(child) for child in p])

    def start(self):
        p = self.plan()
        # Prepare project environment.
        return tasks.execute_plan(p)

    def print_plan(self):
        p = self.plan()
        print("Number of actions to execute: {}".format(self.num_actions))
        print(*p)
