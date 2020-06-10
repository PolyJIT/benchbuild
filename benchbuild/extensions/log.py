import logging

from benchbuild.extensions import base
from benchbuild.utils import run
from benchbuild.utils.cmd import cat

LOG = logging.getLogger(__name__)


class LogTrackingMixin:
    """Add log-registering capabilities to extensions."""
    _logs = []

    def add_log(self, path):
        """
        Add a log to the tracked list.

        Args:
            path (str): Filename of a new log we want to track.
        """
        self._logs.append(path)

    @property
    def logs(self):
        """Return list of tracked logs."""
        return self._logs


class LogAdditionals(base.Extension):
    """Log any additional log files that were registered."""

    def __call__(self, *args, **kwargs):
        if not self.next_extensions:
            return None

        res = self.call_next(*args, **kwargs)
        _cat = run.watch(cat)

        for ext in self.next_extensions:
            if issubclass(ext.__class__, (LogTrackingMixin)):
                for log in ext.logs:
                    LOG.debug("Dumping content of '%s'.", log)
                    _cat(log)
                    LOG.debug("Dumping content of '%s' complete.", log)

        return res

    def __str__(self):
        return "Dump additional log files"
