"""
Register reports for an experiment
"""
import importlib
import logging
import typing as t
import uuid

import attr

from benchbuild.settings import CFG
from benchbuild.utils import schema

LOG = logging.getLogger(__name__)


class ReportRegistry(type):
    reports = {}

    def __init__(cls, name, bases, _dict):
        super(ReportRegistry, cls).__init__(name, bases, _dict)
        if cls.NAME is not None:
            ReportRegistry.reports[cls.NAME] = cls


def load_experiment_ids_from_names(session, names):
    from sqlalchemy import func, column
    from sqlalchemy.sql import select, bindparam

    exps = select([column('id')]).\
        select_from(
            func.experiments(bindparam('names'))
        )
    r1 = session.execute(exps.unique_params(names=names))
    return r1.fetchall()


@attr.s
class Report(metaclass=ReportRegistry):

    SUPPORTED_EXPERIMENTS = []
    NAME = None

    def __new__(cls, *args, **kwargs):
        del args, kwargs  # Temporarily unused
        new_self = super(Report, cls).__new__(cls)
        if not cls.SUPPORTED_EXPERIMENTS:
            raise AttributeError(
                "{0} @ {1} does not define a SUPPORTED_EXPERIMENTS attribute".
                format(cls.__name__, cls.__module__))

        if cls.NAME is None:
            raise AttributeError(
                "{0} @ {1} does not define a NAME attribute".format(
                    cls.__name__, cls.__module__))
        new_self.name = cls.NAME
        return new_self

    experiment_name = attr.ib()
    exp_ids = attr.ib()
    out_path = attr.ib()
    session = attr.ib()

    name = attr.ib(
        default=attr.Factory(lambda self: type(self).NAME, takes_self=True))

    supported_experiments = attr.ib(
        default=attr.Factory(lambda self: type(self).NAME, takes_self=True))

    experiment_ids = attr.ib(default=None)

    def __attrs_post_init__(self):
        if not self.exp_ids:
            exp_ids = load_experiment_ids_from_names(self.session, [
                exp for exp in self.SUPPORTED_EXPERIMENTS
                if exp == self.experiment_name
            ])
            exp_ids = [v[0] for v in exp_ids]
        else:
            exp_ids = [uuid.UUID(v) for v in self.exp_ids]
        self.experiment_ids = exp_ids


def discovered() -> t.Dict[str, Report]:
    """Return all discovered projects."""
    return ReportRegistry.reports
