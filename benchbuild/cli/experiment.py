"""Subcommand for experiment handling."""
import sqlalchemy as sa
from plumbum import cli

from benchbuild import experiment
from benchbuild.cli.main import BenchBuild
from benchbuild.utils import schema


@BenchBuild.subcommand("experiment")
class BBExperiment(cli.Application):
    """Manage BenchBuild's known experiments."""

    def main(self):
        if not self.nested_command:
            self.help()


@BBExperiment.subcommand("view")
class BBExperimentView(cli.Application):
    """View available experiments."""

    def main(self):
        all_exps = experiment.discovered()
        for exp_cls in all_exps.values():
            print(exp_cls.NAME)
            docstring = exp_cls.__doc__ or "-- no docstring --"
            print(("    " + docstring))


def get_template():
    from jinja2 import Environment, PackageLoader
    env = Environment(trim_blocks=True,
                      lstrip_blocks=True,
                      loader=PackageLoader('benchbuild', 'utils/templates'))
    return env.get_template('experiment_show.txt.inc')


def render_experiment(_experiment):
    template = get_template()
    sess = schema.Session()

    return template.render(name=_experiment.name,
                           description=_experiment.description,
                           start_date=_experiment.begin,
                           end_date=_experiment.end,
                           id=_experiment.id,
                           num_completed_runs=get_completed_runs(
                               sess, _experiment),
                           num_failed_runs=get_failed_runs(sess, _experiment))


def experiments_from_db(session):
    return session.query(schema.Experiment).all()


def get_completed_runs(session, exp):
    return session.query(sa.func.count(schema.Run.id)).\
        filter(schema.Run.experiment_group == exp.id).\
        filter(schema.Run.status == 'completed').scalar()


def get_failed_runs(session, exp):
    return session.query(sa.func.count(schema.Run.id)).\
        filter(schema.Run.experiment_group == exp.id).\
        filter(schema.Run.status != 'completed').scalar()
