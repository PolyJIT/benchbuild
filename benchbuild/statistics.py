"""
Handle all statsitic related classes and methods.
"""
import logging

from benchbuild.extensions import Extension
from benchbuild.utils.schema import Session

# The import of scipy and all of its usages are commented out, since its import
# takes too much time for the buildbot. To use the statistics uncomment the
# import and the line containing the stats.ttest function of scipy.
# import scipy

LOG = logging.getLogger(__name__)
TIMEOUT = 1


class Statistics(Extension):
    """
    Extend a run to be repeated until it reaches a statistically significance
    specified by the user.

    An example on how to use this extension can be found in the Pollytest
    Experiment.
    """

    def __init__(self, project, experiment, *extensions, config=None):
        self.project = project
        self.experiment = experiment

        super().__init__(*extensions, config=config)

    def t_test(self, *results, significance=0.95):
        """
        Runs a t-test on a given set of results.

        Returns:
            True if the null hypothesis that the result was not significant
            was rejected, False otherwise.
        """
        for result in results:
            del result  # Unused temporarily
            t_statistic = 0
            p_value = 0
            #t_statistic, p_value = scipy.stats.ttest_1samp(result, TRUE_MU)
            LOG.debug("t-statistic = %f, pvalue = %f", t_statistic, p_value)
        return p_value >= 1 - significance

    def __call__(self, *args, timeout=TIMEOUT, **kwargs):
        """
        The call of this extension runs the following extensions until the
        timeout was reached or a run was significant enough to withdraw the
        nullhypothesis.

        Kwargs:
            timeout: The amount of trys the user wants to give the experiment
                     before it gets interrupted.
        Returns:
            The run info object after executing the
            afterwards following extensions.
        """
        iterator = 0
        session = Session()

        while iterator < timeout:
            #get an run_info object after executing the run with its extensions
            ri_object = self.call_next(*args, **kwargs)

            #check if the experiment defines the result function
            if hasattr(self.experiment, 'res_func'):
                results = self.experiment.res_func(ri_object)
                if self.t_test(results):
                    LOG.info("The run was significant.")
                    break

                #check if this was the last iteration
                if iterator == (timeout - 1):
                    LOG.warning(
                        "No significant run happened before the timeout!"
                    )
                iterator += 1

            # no need to repeat the run without a result function
            else:
                break

        #Commit the database session containing all runs
        session.commit()

        LOG.info("Overall one command was executed %s times.", iterator)
        return ri_object
