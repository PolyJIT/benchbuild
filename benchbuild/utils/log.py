import logging

from rich.console import Console
from rich.logging import RichHandler

from benchbuild import settings


def configure_migrate_log():
    migrate_log = logging.getLogger("migrate.versioning")
    migrate_log.setLevel(logging.ERROR)
    migrate_log.propagate = True


def configure_plumbum_log():
    plumbum_format = logging.Formatter('$> %(message)s')
    handler = RichHandler(
        rich_tracebacks=True,
        show_time=False,
        show_level=False,
        console=Console(stderr=True)
    )
    handler.setFormatter(plumbum_format)

    plumbum_local = logging.getLogger("plumbum.local")
    plumbum_local.propagate = False
    if settings.CFG["debug"]:
        plumbum_local.setLevel(logging.DEBUG)
    plumbum_local.addHandler(handler)


def configure_parse_log():
    log = logging.getLogger("parse")
    log.setLevel(logging.CRITICAL)


def configure():
    """Load logging configuration from our own defaults."""
    log_levels = {
        5: logging.NOTSET,
        4: logging.DEBUG,
        3: logging.INFO,
        2: logging.WARNING,
        1: logging.ERROR,
        0: logging.ERROR
    }

    handler = RichHandler(
        rich_tracebacks=True,
        show_time=False,
        show_level=False,
        console=Console(stderr=True)
    )
    logging.captureWarnings(True)
    root_logger = logging.getLogger()
    if settings.CFG["debug"]:
        details_format = logging.Formatter(
            '%(name)s (%(filename)s:%(lineno)s) [%(levelname)s] %(message)s'
        )
        details_hdl = handler
        details_hdl.setFormatter(details_format)
        root_logger.addHandler(details_hdl)
    else:
        brief_format = logging.Formatter('%(message)s')
        console_hdl = handler
        console_hdl.setFormatter(brief_format)
        root_logger.addHandler(console_hdl)
    root_logger.setLevel(log_levels[int(settings.CFG["verbosity"])])

    configure_plumbum_log()
    configure_migrate_log()
    configure_parse_log()


def set_defaults():
    """Configure the loggers default settings."""
