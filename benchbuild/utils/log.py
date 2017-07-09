import logging
import logging.config as lc
from benchbuild import settings

LOG_DICT = {
    "version": 1,
    "formatters": {
        "brief": {
            'class': 'logging.Formatter',
            'format': '%(message)s'
        },
        "details": {
            'class': 'logging.Formatter',
            'format': '%(name)s (%(filename)s:%(lineno)s) [%(levelname)s] %(message)s'
        },
        "plumbum": {
            'class': 'logging.Formatter',
            'format': '--- %(message)s'
        }
    },
    "handlers": {
        "console": {
            'class': 'logging.StreamHandler',
            'formatter': 'brief'
        },
        "details": {
            'class': 'logging.StreamHandler',
            'formatter': 'details'
        },
        "plumbum": {
            'class': 'logging.StreamHandler',
            'formatter': 'plumbum'
        }
    },
    "loggers": {
        "benchbuild": {'propagate': False},
        "plumbum.local": {'level': 'DEBUG',
                          'handlers': ['plumbum'],
                          'propagate': False},
        "sqlalchemy.engine": {
            "level": "ERROR"
        },
        "parse": {
            'level': 'WARN',
            'handlers': ['console'],
        },
    },
    "root": {
        "level": 'DEBUG',
        "handlers": ["console"]
    }
}


def configure():
    """Load logging configuration from our own defaults."""
    debug = settings.CFG["debug"].value()
    if debug:
        LOG_DICT["root"]["handlers"] = ["details"]
    lc.dictConfig(LOG_DICT)


def set_defaults():
    """Configure the loggers default settings."""
    log_levels = {
        3: logging.DEBUG,
        2: logging.INFO,
        1: logging.WARNING,
        0: logging.ERROR
    }

    logging.captureWarnings(True)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_levels[settings.CFG["verbosity"].value()])
