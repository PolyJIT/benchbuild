import csv
import os
import sqlalchemy as sa
from benchbuild.reports import Report
from benchbuild.experiment import ExperimentRegistry


class StatusReport(Report):
    SUPPORTED_EXPERIMENTS = list(ExperimentRegistry.experiments.keys())
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
        print("I found the following matching experiment ids")
        print("  \n".join([str(x) for x in self.experiment_ids]))

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
