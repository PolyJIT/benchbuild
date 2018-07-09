"""
Remove unneeded GlobalConfig table.

This table can and should be reintroduced by an experiment that requires it.
"""
from sqlalchemy import Table, Column, ForeignKey, Integer, String
from benchbuild.utils.schema import metadata, GUID

META = metadata()
GLOBAL = Table('globalconfig', META,
               Column(
                   'experiment_group',
                   GUID(as_uuid=True),
                   ForeignKey(
                       'experiment.id', onupdate="CASCADE",
                       ondelete="CASCADE"),
                   primary_key=True), Column('name', String, primary_key=True),
               Column('value', String))


def upgrade(migrate_engine):
    META.bind = migrate_engine
    GLOBAL.drop()


def downgrade(migrate_engine):
    META.bind = migrate_engine
    GLOBAL.create()
