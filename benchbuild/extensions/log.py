import logging
import typing as tp

from benchbuild.extensions import base
from benchbuild.utils import run
from benchbuild.utils.cmd import cat

LOG = logging.getLogger(__name__)


class LogTrackingMixin:
    """Add log-registering capabilities to extensions."""
    _logs: tp.List[str] = []

    def add_log(self, path: str) -> None:
        """
        Add a log to the tracked list.

        Args:
            path (str): Filename of a new log we want to track.
        """
        self._logs.append(path)

    @property
    def logs(self) -> tp.List[str]:
        """Return list of tracked logs."""
        return self._logs


class LogAdditionals(base.Extension):
    """Log any additional log files that were registered."""

    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> tp.List[run.RunInfo]:
        if not self.next_extensions:
            return []

        res = self.call_next(*args, **kwargs)
        _cat = run.watch(cat)

        for ext in self.next_extensions:
            if isinstance(ext, LogTrackingMixin):
                for log in ext.logs:
                    LOG.debug("Dumping content of '%s'.", log)
                    _cat(log)
                    LOG.debug("Dumping content of '%s' complete.", log)

        return res

    def __str__(self) -> str:
        return "Dump additional log files"
