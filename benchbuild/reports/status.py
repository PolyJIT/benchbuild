import csv
import os
import sqlalchemy as sa
import pandas as pd
from benchbuild.reports import Report
from benchbuild.experiment import ExperimentRegistry


class StatusReport(Report):
    SUPPORTED_EXPERIMENTS = list(ExperimentRegistry.experiments.keys())
    NAME = "status"
    QUERY_STATUS = \
        sa.sql.select([
            sa.column('name'),
            sa.column('_group'),
            sa.column('status'),
            sa.column('runs')
        ]).\
        select_from(
            sa.func.exp_status(sa.sql.bindparam('exp_ids'))
        )

    def report(self):
        qry = StatusReport.\
            QUERY_STATUS.unique_params(exp_ids=self.experiment_ids)
        yield ("status",
               ('project', 'group', 'status', 'runs'),
               self.session.execute(qry).fetchall())

    def generate(self):
        for name, header, data in self.report():
            fname = os.path.basename(self.out_path)

            fname = "{prefix}_{name}{ending}".format(
                prefix=os.path.splitext(fname)[0],
                ending=os.path.splitext(fname)[-1],
                name=name)
            with open(fname, 'w') as csv_out:
                print("Writing '{0}'".format(csv_out.name))
                csv_writer = csv.writer(csv_out)
                csv_writer.writerows([header])
                csv_writer.writerows(data)


class FullDump(Report):
    """Generate a dump of all rows associated with this experiment."""
    SUPPORTED_EXPERIMENTS = list(ExperimentRegistry.experiments.keys())
    NAME = "full"

    def exp_name(self):
        import benchbuild.utils.schema as s
        exp_name = "multiple"
        if len(self.experiment_ids) == 1:
            q = self.session.query(s.Experiment)\
                    .filter(s.Experiment.id.in_(self.experiment_ids))\
                    .distinct()
            exp_name = q.one().name
        return exp_name

    def report(self):
        import benchbuild.utils.schema as s
        tables = s.BASE.metadata.tables
        required_tables = []
        for _, table in tables.items():
            if 'run_id' in table.columns and \
               table.name != 'log':
                required_tables.append(table)

        run = tables['run']
        joined = run
        for table in required_tables:
            joined = joined.outerjoin(
                table, run.columns.id == table.c['run_id'])
        joined = joined.select(use_labels=True).where(
            run.columns.experiment_group.in_(
                self.experiment_ids)
        )

        return pd.read_sql_query(
            joined, self.session.connection(), chunksize=100)

    def generate(self):
        """
        Fetch all rows associated with this experiment.

        This will generate a huge .csv.
        """
        exp_name = self.exp_name()

        fname = os.path.basename(self.out_path)
        fname = "{exp}_{prefix}_{name}{ending}".format(
            exp=exp_name,
            prefix=os.path.splitext(fname)[0],
            ending=os.path.splitext(fname)[-1],
            name="full")
        first = True
        for chunk in self.report():
            print("Writing chunk to :'{0}'".format(fname))
            chunk.to_csv(fname, header=first, mode='a')
            first = False
