"""
The task module distributes benchbuild's excution plans over processes.
"""
import benchbuild.utils.actions as actns


def execute_plan(plan):
    """"Execute the plan.

    Args:
        plan (:obj:`list` of :obj:`actions.Step`): The plan we want to execute.

    Returns:
        (:obj:`list` of :obj:`actions.Step`): A list of failed actions.
    """
    results = [action() for action in plan]
    return [result for result in results if actns.step_has_failed(result)]


def generate_plan(exps, prjs):
    """
    Generate an execution plan for the given experimetns and projects.

    Args:
        exps: dictionary of experiment names and their associated experiment
              class.
        prjs: list of projects to populate each experiment with.

    Returns:
        a list of experiment actions suitable for execution.
    """
    for exp_cls in exps.values():
        exp = exp_cls(projects=prjs)
        eactn = actns.Experiment(obj=exp, actions=exp.actions())
        yield eactn
