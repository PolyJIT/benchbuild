import functools
import logging
import signal
import sys


LOG = logging.getLogger(__name__)


class CleanupOnSignal(object):
    __stored_procedures = []
    @property
    def stored_procedures(self):
        return self.__stored_procedures

    def register(self, callable, *args, **kwargs):
        new_func = functools.partial(callable, *args, **kwargs)
        LOG.debug("Registering new function %r", new_func)
        self.__stored_procedures.append(new_func)

    def __call__(self):
        for proc in self.stored_procedures:
            LOG.debug("Running stored cleanup procedure: %r", proc)
            proc()

handlers = CleanupOnSignal()

def __handle_sigterm(signum, frame):
    LOG.debug("Got SIGTERM, running cleanup handlers")
    handlers()
    sys.exit(signum)

signal.signal(signal.SIGTERM, __handle_sigterm)
