import functools
import logging
import signal
import sys

LOG = logging.getLogger(__name__)


class CleanupOnSignal(object):
    __stored_procedures = {}

    @property
    def stored_procedures(self):
        return self.__stored_procedures

    def register(self, callback, *args, **kwargs):
        new_func = functools.partial(callback, *args, **kwargs)
        self.__stored_procedures[callback] = new_func

    def deregister(self, callback):
        del self.__stored_procedures[callback]

    def __call__(self):
        for k in self.stored_procedures:
            LOG.debug("Running stored cleanup procedure: %r", k)
            self.stored_procedures[k]()

handlers = CleanupOnSignal()

def __handle_sigterm(signum, frame):
    del frame
    LOG.debug("Got SIGTERM, running cleanup handlers")
    handlers()
    sys.exit(signum)

signal.signal(signal.SIGTERM, __handle_sigterm)
