import logging
import logging.config as lc
from benchbuild import settings

__LOG_DICT = {
    "version": 1,
    "formatters": {
        "brief": {
            'class': 'logging.Formatter',
            'format': '%(message)s'
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
        "plumbum": {
            'class': 'logging.StreamHandler',
            'formatter': 'plumbum'
        }
    },
    "loggers": {
        "benchbuild": {},
        "benchbuild.steps": {},
        "plumbum.local": {'level': 'DEBUG',
                          'handlers': ['plumbum'],
                          'propagate': False},
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
    lc.dictConfig(__LOG_DICT)


def set_defaults():
    """Configure the loggers default settings."""
    log_levels = {
        3: logging.DEBUG,
        2: logging.INFO,
        1: logging.WARNING,
        0: logging.ERROR
    }

    logging.captureWarnings(True)
    LOG = logging.getLogger()
    LOG.setLevel(log_levels[settings.CFG["verbosity"].value()])
