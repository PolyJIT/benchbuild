"""
A test experiment for PolyJIT.

This experiment should only be used to test various features of PolyJIT. It
provides only 1 configuration (maximum number of cores) and tests 2 run-time
execution profiles of PolyJIT:
  1) PolyJIT enabled, with specialization
  2) PolyJIT enabled, without specialization
"""
import csv
import logging
import os
import uuid

import sqlalchemy as sa

from benchbuild.experiments.polyjit import PolyJIT
from benchbuild.reports import Report
from benchbuild.settings import CFG

import benchbuild.extensions as ext
from benchbuild.experiments.polyjit import \
    (EnablePolyJIT, DisablePolyJIT, RegisterPolyJITLogs)

LOG = logging.getLogger()


class Test(PolyJIT):
    """
    An experiment that executes all projects with PolyJIT support.

    This is our default experiment for speedup measurements.
    """

    NAME = "pj-test"

    def actions_for_project(self, p):
        p = PolyJIT.init_project(p)
        p.run_uuid = uuid.uuid4()
        jobs = int(CFG["jobs"].value())
        p.cflags += ["-Rpass-missed=polli*",
                     "-mllvm", "-stats",
                     "-mllvm", "-polly-num-threads={0}".format(jobs)]

        cfg_with_jit = {
            'jobs': jobs,
            "cflags": p.cflags,
            "cores": str(jobs - 1),
            "cores-config": str(jobs),
            "recompilation": "enabled",
            "specialization": "enabled"
        }

        cfg_without_jit = {
            'jobs': jobs,
            "cflags": p.cflags,
            "cores": str(jobs - 1),
            "cores-config": str(jobs),
            "recompilation": "enabled",
            "specialization": "disabled"
        }

        p.runtime_extension = \
            ext.LogAdditionals(
                RegisterPolyJITLogs(
                    ext.RunWithTime(
                        EnablePolyJIT(
                            ext.RuntimeExtension(p, self, config=cfg_with_jit)),
                        DisablePolyJIT(
                            ext.RuntimeExtension(p, self, config=cfg_without_jit))
                    )))
        return Test.default_runtime_actions(p)


class StatusReport(Report):

    SUPPORTED_EXPERIMENTS = ["pj-test", "pj-seq-test", "raw", "pj", "pj-raw", "pollytest"]
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

            with open("{prefix}_{name}{ending}".format(
                prefix=os.path.splitext(fname)[0],
                ending=os.path.splitext(fname)[-1],
                name=name), 'w') as csv_out:
                print("Writing '{0}'".format(csv_out.name))
                csv_writer = csv.writer(csv_out)
                csv_writer.writerows([header])
                csv_writer.writerows(data)


class TestReport(Report):

    SUPPORTED_EXPERIMENTS = ["pj-test"]

    QUERY_TOTAL = \
        sa.sql.select([
            sa.column('project'),
            sa.column('domain'),
            sa.column('speedup'),
            sa.column('ohcov_0'),
            sa.column('ohcov_1'),
            sa.column('dyncov_0'),
            sa.column('dyncov_1'),
            sa.column('cachehits_0'),
            sa.column('cachehits_1'),
            sa.column('variants_0'),
            sa.column('variants_1'),
            sa.column('codegen_0'),
            sa.column('codegen_1'),
            sa.column('scops_0'),
            sa.column('scops_1'),
            sa.column('t_0'),
            sa.column('o_0'),
            sa.column('t_1'),
            sa.column('o_1')
        ]).\
        select_from(
            sa.func.pj_test_eval(sa.sql.bindparam('exp_ids'))
        )

    QUERY_REGION = \
        sa.sql.select([
            sa.column('project'),
            sa.column('region'),
            sa.column('cores'),
            sa.column('t_polly'),
            sa.column('t_polyjit'),
            sa.column('speedup')
        ]).\
        select_from(
            sa.func.pj_test_region_wise(sa.sql.bindparam('exp_ids'))
        )

    def report(self):
        print("I found the following matching experiment ids")
        print("  \n".join([str(x) for x in self.experiment_ids]))

        qry = TestReport.QUERY_TOTAL.unique_params(exp_ids=self.experiment_ids)
        yield ("complete",
               ('project', 'domain',
                'speedup',
                'ohcov_0', 'ocov_1',
                'dyncov_0', 'dyncov_1',
                'cachehits_0', 'cachehits_1',
                'variants_0', 'variants_1',
                'codegen_0', 'codegen_1',
                'scops_0', 'scops_1',
                't_0', 'o_0', 't_1', 'o_1'),
               self.session.execute(qry).fetchall())
        qry = TestReport.QUERY_REGION.unique_params(exp_ids=self.experiment_ids)
        yield ("regions",
               ('project', 'region', 'cores', 'T_Polly', 'T_PolyJIT',
                'speedup'),
               self.session.execute(qry).fetchall())

    def generate(self):
        for name, header, data in self.report():
            fname = os.path.basename(self.out_path)

            with open("{prefix}_{name}{ending}".format(
                prefix=os.path.splitext(fname)[0],
                ending=os.path.splitext(fname)[-1],
                name=name), 'w') as csv_out:
                print("Writing '{0}'".format(csv_out.name))
                csv_writer = csv.writer(csv_out)
                csv_writer.writerows([header])
                csv_writer.writerows(data)
