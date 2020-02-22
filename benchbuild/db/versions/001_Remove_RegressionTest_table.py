"""
Remove unneeded Regressions table.

This table can and should be reintroduced by an experiment that requires it.
"""
import sqlalchemy as sa
from sqlalchemy import Column, ForeignKey, Integer, String, Table

from benchbuild.utils.schema import exceptions, metadata

META = metadata()
REGRESSION = Table(
    'regressions', META,
    Column('run_id',
           Integer,
           ForeignKey('run.id', onupdate="CASCADE", ondelete="CASCADE"),
           index=True,
           primary_key=True), Column('name', String), Column('module', String),
    Column('project_name', String))


def upgrade(migrate_engine):

    @exceptions(
        error_is_fatal=False,
        error_messages={
            sa.exc.ProgrammingError:
                "Removing table 'Regressions' failed. Please delete the table manually"
        })
    def do_upgrade():
        META.bind = migrate_engine
        REGRESSION.drop()

    do_upgrade()


def downgrade(migrate_engine):

    @exceptions(error_messages={
        sa.exc.ProgrammingError: "Adding table 'Regressions' failed."
    })
    def do_downgrade():
        META.bind = migrate_engine
        REGRESSION.create()

    do_downgrade()
