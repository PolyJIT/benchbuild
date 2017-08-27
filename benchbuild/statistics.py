"""
Handle all statsitic related classes and methods.
"""
import logging
import parse

from statistics import median
from benchbuild.extensions import Extension
from benchbuild.utils.schema import Session
from benchbuild.utils.run import track_execution
# from scipy import stats

LOG = logging.getLogger(__name__)

TIMEOUT = 5
NULLHYPO = 0.0 # means the results are not related to each other
P_VAL = 0.6 # with a chance of 60% the null hypothesis is wrong

def dist_func(run_info):
    """
    The default p value calculation of the experiment under the assumption
    that the results are normally distributed in a two-tailed test static.
    The p value gets calculated based on one sample array of results.
    This sample pool is created by putting all values of a measured project
    into a list.
    """
    values = []
    p_val = 0.0
    if run_info.db_run.status == "completed":
        results = []
        result_pattern = parse.compile("{value:d} {component} - {desc}\n")

        for line in run_info.stderr.split("\n"):
            if line:
                try:
                    results = result_pattern.search(line + "\n")
                except ValueError:
                    LOG.warning("Could not parse: '" + line + "'\n")

        for stat in results:
            values.append(stat["value"])
            print("value added to the array: " + stat["value"])
#        _, p_val = stats.ttest_1samp(values, NULLHYPO)
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

    def __call__(self, cc, *args, min_p_val=P_VAL, timeout=TIMEOUT, **kwargs):
        """
        The call of this extension runs the following extensions until a the
        p value the user specified is reached or the run times out.

        Args:
            cc: The compiler commando that becomes clang.
        Kwargs:
            min_p_val: The minimum p value the user wants to reach with
                       the running experiment.
            timeout: The amount of trys the user wants to give the experiment
                     before it gets interrupted.
        Returns:
            The run after executing the afterwards following extensions.
        """
        calculated_ps = []
        cur_p_val = 0.0
        iterator = 1
        res = None
        session = Session()

        LOG.info("Started experiment until it has reached the wanted p value.")
        clang = cc["-mllvm", "-stats"]
        while iterator < timeout and cur_p_val < min_p_val:
            results = self.call_next(cc, *args, **kwargs)
            if results is not None:
                with track_execution(clang, self.project, self.experiment):
                    run_info = results[0]()
                cur_p_val = dist_func(run_info)
                LOG.debug(
                    "In the %s. iteration a p-value of %s was calculated.",
                    iterator, cur_p_val)
                calculated_ps.append(cur_p_val)
                session.commit()
            else:
                LOG.info("There were no following extensions to run.")
                break
            iterator += 1

        if iterator < TIMEOUT and min_p_val <= cur_p_val:
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
