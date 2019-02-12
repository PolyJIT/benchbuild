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
