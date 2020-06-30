"""
Remove unneeded GlobalConfig table.

This table can and should be reintroduced by an experiment that requires it.
"""

import sqlalchemy as sa
from sqlalchemy import Column, ForeignKey, String, Table

from benchbuild.utils.schema import GUID, exceptions, metadata

META = metadata()
GLOBAL = Table(
    'globalconfig', META,
    Column('experiment_group',
           GUID(as_uuid=True),
           ForeignKey('experiment.id', onupdate="CASCADE", ondelete="CASCADE"),
           primary_key=True), Column('name', String, primary_key=True),
    Column('value', String))


def upgrade(migrate_engine):

    @exceptions(
        error_is_fatal=False,
        error_messages={
            sa.exc.ProgrammingError:
                "Removing table 'globalconfig' failed. Please delete the table manually"
        })
    def do_upgrade():
        META.bind = migrate_engine
        GLOBAL.drop()

    do_upgrade()


def downgrade(migrate_engine):

    @exceptions(error_messages={
        sa.exc.ProgrammingError: "Adding table 'globalconfig' failed."
    })
    def do_downgrade():
        META.bind = migrate_engine
        GLOBAL.create()

    do_downgrade()
