"""
Handle all statsitic related classes and methods.
"""
import logging

from benchbuild.extensions import Extension
from benchbuild.utils.schema import Session

from numpy import median
from scipy import stats

LOG = logging.getLogger(__name__)

TIMEOUT = 5
POPMEAN = 0.0
P_VAL = 0.9

def dist_func(results):
    """
    The default p value calculation of the experiment under the assumption
    that the results are normally distributed.
    """
    _, p_val = stats.ttest_1samp(results, POPMEAN)
    return p_val


class Statistics(Extension):
    """
    Extend a run to be repeated until it reaches a statistically significance
    specified by the user.
    """
    def __init__(self, project, experiment, *extensions, config=None, **kwargs):
        self.project = project
        self.experiment = experiment

        super(Statistics, self).__init__(*extensions, config=config)

    def __call__(self, *args, min_p_val=P_VAL, results=[], **kwargs):
        """
        The call of this extension runs the following extensions until a the
        p value the user specified is reached or the run times out.

        Kwargs:
            min_p_val: The minimum p value the user wants to reach with
                       the running experiment.
        Returns:
            The run after executing the afterwards following extensions.
        """
        session = Session()
        iterator = 0
        res = None
        cur_p_val = 0
        calculated_ps = []

        LOG.info("Started experiment until it has reached the wanted p value.")
        while iterator < TIMEOUT and cur_p_val < min_p_val:
            iterator += 1
            LOG.debug("Iteration: %s", str(iterator))
            cur_p_val = dist_func(results)
            calculated_ps.append(cur_p_val)
            res = self.call_next(*args, **kwargs)
            session.commit()

        if iterator < TIMEOUT:
            LOG.info("The statistically significance of p = %s was reached.",
                     cur_p_val)
        else:
            LOG.info("The experiment did not manage to reach the " +
                     " statistically significance of %s before timing out.",
                     min_p_val)

        median_p = median(calculated_ps)
        LOG.info("Overall a median of %s, " +
                 "was reached by all calculated p values.", median_p)
        return res
