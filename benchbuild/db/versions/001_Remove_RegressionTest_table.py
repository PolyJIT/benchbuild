"""
Remove unneeded Regressions table.

This table can and should be reintroduced by an experiment that requires it.
"""
from sqlalchemy import Table, Column, ForeignKey, Integer, String
from benchbuild.utils.schema import metadata

META = metadata()
REGRESSION = Table('regressions', META,
                   Column(
                       'run_id',
                       Integer,
                       ForeignKey(
                           'run.id', onupdate="CASCADE", ondelete="CASCADE"),
                       index=True,
                       primary_key=True), Column('name', String),
                   Column('module', String), Column('project_name', String))


def upgrade(migrate_engine):
    META.bind = migrate_engine
    REGRESSION.drop()


def downgrade(migrate_engine):
    META.bind = migrate_engine
    REGRESSION.create()
