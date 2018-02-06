"""
Handle all statsitic related classes and methods.
"""
import logging

from benchbuild.extensions import Extension
from benchbuild.utils.schema import Session

LOG = logging.getLogger(__name__)

TIMEOUT = 3

class Statistics(Extension):
    """
    Extend a run to be repeated until it reaches a statistically significance
    specified by the user.

    An example on how to use this extension can be found in the Pollytest
    Experiment.
    """
    def __init__(self, project, experiment, *extensions, config=None, **kwargs):
        self.project = project
        self.experiment = experiment

        super(Statistics, self).__init__(*extensions, config=config)

    def __call__(self, *args, timeout=TIMEOUT, **kwargs):
        """
        The call of this extension runs the following extensions untile the
        timeout was reached.

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
            results = self.call_next(*args, **kwargs)
            iterator += 1
        session.commit()

        LOG.info("Overall one command was executed %s, " +
                 "times.", iterator)
        return results
