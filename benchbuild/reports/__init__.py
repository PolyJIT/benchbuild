"""
Register reports for an experiment
"""
from benchbuild.settings import CFG
import logging
import importlib


def discover():
    """
    Import all experiments listed in *_PLUGINS_REPORTS.

    Tests:
        >>> from benchbuild.settings import CFG
        >>> from benchbuild.reports import discover
        >>> import logging as lg
        >>> import sys
        >>> l = lg.getLogger('benchbuild')
        >>> lg.getLogger('benchbuild').setLevel(lg.DEBUG)
        >>> lg.getLogger('benchbuild').handlers = [lg.StreamHandler(stream=sys.stdout)]
        >>> CFG["plugins"]["reports"] = ["benchbuild.non.existing", "benchbuild.reports.raw"]
        >>> discover()
        Could not find 'benchbuild.non.existing'
        Found report: benchbuild.reports.raw
    """
    if CFG["plugins"]["autoload"].value():
        log = logging.getLogger('benchbuild')
        report_plugins = CFG["plugins"]["reports"].value()
        for ep in report_plugins:
            try:
                importlib.import_module(ep)
                log.debug("Found report: {0}".format(ep))
            except ImportError:
                log.error("Could not find '{0}'".format(ep))


class ReportRegistry(type):
    reports = {}

    def __init__(cls, name, bases, dict):
        super(ReportRegistry, cls).__init__(name, bases, dict)
        if cls.SUPPORTED_EXPERIMENTS is not None:
            for exp in cls.SUPPORTED_EXPERIMENTS:
                if exp in ReportRegistry.reports:
                    ReportRegistry.reports[exp].append(cls)
                else:
                    ReportRegistry.reports[exp] = [cls]


class Report(object, metaclass=ReportRegistry):

    SUPPORTED_EXPERIMENTS = None

    def __new__(cls, *args, **kwargs):
        new_self = super(Report, cls).__new__(cls)
        if cls.SUPPORTED_EXPERIMENTS is None:
            raise AttributeError(
                "{0} @ {1} does not define a SUPPORTED_EXPERIMENTS attribute"
                .format(cls.__name__, cls.__module__))
        new_self.experiments = cls.SUPPORTED_EXPERIMENTS
        return new_self

    def __init__(self, exp_ids, out_path):
        import benchbuild.utils.schema as schema
        self.experiment_ids = exp_ids
        self.out_path = out_path
        self.session = schema.Session()
