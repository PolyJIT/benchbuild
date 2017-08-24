"""
Register reports for an experiment
"""
import importlib
import logging
from benchbuild.settings import CFG

LOG = logging.getLogger(__name__)


def discover():
    """
    Import all experiments listed in *_PLUGINS_REPORTS.

    Tests:
        >>> from benchbuild.settings import CFG
        >>> from benchbuild.reports import discover
        >>> import logging as lg
        >>> import sys
        >>> l = lg.getLogger('benchbuild')
        >>> l.setLevel(lg.DEBUG)
        >>> l.handlers = [lg.StreamHandler(stream=sys.stdout)]
        >>> CFG["plugins"]["reports"] = ["benchbuild.non.existing", "benchbuild.reports.raw"]
        >>> discover()
        Could not find 'benchbuild.non.existing'
        Found report: benchbuild.reports.raw
    """
    if CFG["plugins"]["autoload"].value():
        report_plugins = CFG["plugins"]["reports"].value()
        for ep in report_plugins:
            try:
                importlib.import_module(ep)
                LOG.debug("Found report: %s", ep)
            except ImportError:
                LOG.error("Could not find '%s'", ep)


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


def load_experiment_ids_from_names(session, names):
    from sqlalchemy import func, column
    from sqlalchemy.sql import select, bindparam

    exps = select([column('id')]).\
        select_from(
            func.experiments(bindparam('names'))
        )
    r1 = session.execute(
        exps.unique_params(names=names)
    )
    return r1.fetchall()


class Report(object, metaclass=ReportRegistry):

    SUPPORTED_EXPERIMENTS = []

    def __new__(cls, *args, **kwargs):
        new_self = super(Report, cls).__new__(cls)
        if cls.SUPPORTED_EXPERIMENTS is None:
            raise AttributeError(
                "{0} @ {1} does not define a SUPPORTED_EXPERIMENTS attribute"
                .format(cls.__name__, cls.__module__))
        new_self.experiments = cls.SUPPORTED_EXPERIMENTS
        return new_self

    def __init__(self, exp_name, exp_ids, out_path):
        import benchbuild.utils.schema as schema
        import uuid
        self.out_path = out_path
        self.session = schema.Session()
        if not exp_ids:
            exp_ids = load_experiment_ids_from_names(
                self.session,
                [exp for exp in self.SUPPORTED_EXPERIMENTS if exp == exp_name])
            exp_ids = [v[0] for v in exp_ids]
        else:
            exp_ids = [uuid.UUID(v) for v in exp_ids]

        self.experiment_ids = exp_ids
