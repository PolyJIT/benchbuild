import csv
import os
import sqlalchemy as sa
import benchbuild.utils.schema as schema
import benchbuild.reports as reports
import benchbuild.experiment as exp
import benchbuild.experiments.compilestats as cs

import pandas as pd

query = sa.orm.Query
select = sa.sql.select
join = sa.sql.join
outerjoin = sa.sql.outerjoin
any_ = sa.sql.expression.any_
sum_ = sa.func.sum

RUN = schema.Run.__table__
CS = cs.CompileStat.__table__

class CompileStatsReport(reports.Report):
    NAME = "compilestats"
    SUPPORTED_EXPERIMENTS = list(exp.ExperimentRegistry.experiments.keys())

    def generate(self):
        exp_ids = self.experiment_ids
        fname = "compilestats_report.csv"

        runs = select([RUN]).where(RUN.c.experiment_group == any_(exp_ids)).alias(name="run_1")
        join_clause = join(runs, CS, runs.c.id == CS.c.run_id)
        q = select(
            [
                runs.c.project_name.label("name"),
                runs.c.project_group.label("group"),
                CS.c.name.label("metric"),
                sum_(CS.c.value).label("value"),
            ]
        ).select_from(join_clause)\
            .group_by(runs.c.project_name, runs.c.project_group, CS.c.name)\
            .order_by(runs.c.project_name, runs.c.project_group)

        report = pd.read_sql(q.selectable, con=self.session.connection())
        print("Writing '", fname, "' ...")
        report.to_csv(fname)