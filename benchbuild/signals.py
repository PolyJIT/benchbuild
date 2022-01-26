import functools
import logging
import signal
import sys
import typing as tp

LOG = logging.getLogger(__name__)

StoredProcedureTy = tp.Callable[..., None]
StoredProceduresTy = tp.Dict[StoredProcedureTy, tp.Callable[[], None]]


class CleanupOnSignal:
    __stored_procedures: StoredProceduresTy = {}

    @property
    def stored_procedures(self) -> StoredProceduresTy:
        return self.__stored_procedures

    def register(
        self, callback: StoredProcedureTy, *args: tp.Any, **kwargs: tp.Any
    ) -> None:
        new_func = functools.partial(callback, *args, **kwargs)
        self.__stored_procedures[callback] = new_func

    def deregister(self, callback: StoredProcedureTy) -> None:
        del self.__stored_procedures[callback]

    def __call__(self) -> None:
        for k, func in self.stored_procedures.items():
            LOG.debug("Running stored cleanup procedure: %r", k)
            func()


handlers = CleanupOnSignal()


def __handle_sigterm(signum: int, frame: tp.Any) -> None:
    del frame
    LOG.debug("Got SIGTERM, running cleanup handlers")
    handlers()
    sys.exit(signum)


signal.signal(signal.SIGTERM, __handle_sigterm)
