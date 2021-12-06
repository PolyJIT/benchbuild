"""
The task module distributes benchbuild's excution plans over processes.
"""
import typing as tp

import benchbuild.utils.actions as actns
from benchbuild import Experiment, Project

ExperimentT = tp.Type[Experiment]
ProjectT = tp.Type[Project]

ExperimentTs = tp.List[ExperimentT]
ProjectTs = tp.List[ProjectT]
Actions = tp.Sequence[actns.Step]
StepResults = tp.List[actns.StepResult]


def execute_plan(plan: Actions) -> StepResults:
    """"Execute the plan.

    Args:
        plan: The plan we want to execute.

    Returns:
        A list failed of StepResults.
    """
    results = [action() for action in plan]
    return [result for result in results if actns.step_has_failed(result)]


def generate_plan(exps: ExperimentTs, prjs: ProjectTs) -> Actions:
    """
    Generate an execution plan for the given experimetns and projects.

    Args:
        exps: list of experiments.
        prjs: list of projects to populate each experiment with.

    Returns:
        a list of experiment actions suitable for execution.
    """
    actions = []
    for exp_cls in exps:
        exp = exp_cls(projects=prjs)
        actions.append(actns.Experiment(exp, actions=exp.actions()))
    return actions
