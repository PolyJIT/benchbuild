import logging
import logging.config

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
        "pprof": {},
        "pprof.steps": {},
        "plumbum.local": {'level': 'DEBUG',
                          'handlers': ['plumbum'],
                          'propagate': False}
    },
    "root": {
        "level": 'WARN',
        "handlers": ["console"]
    }
}


def configure():
    logging.config.dictConfig(__LOG_DICT)
