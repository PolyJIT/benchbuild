"""
Test Maximal Static Expansion.

This tests the maximal static expansion implementation by
Nicholas Bonfante (implemented in LLVM/Polly).
"""
import csv
import logging
import os
import benchbuild.extensions as ext

from benchbuild.experiment import RuntimeExperiment
from benchbuild.utils.run import fetch_time_output
from benchbuild.utils.db import persist_time
from benchbuild.settings import CFG
from benchbuild.reports import Report

import sqlalchemy as sa


LOG = logging.getLogger(__name__)


def mse_persist_time_and_memory(run, session, timings):
    """
    Persist the memory results in the database.

    Args:
        run: The run we attach this timing results to.
        session: The db transaction we belong to.
        timings: The timing measurements we want to store.
    """
    from benchbuild.utils import schema as s

    for timing in timings:
        session.add(s.Metric(name="time.user_s",
                             value=timing[0],
                             run_id=run.id))
        session.add(s.Metric(name="time.system_s",
                             value=timing[1],
                             run_id=run.id))
        session.add(s.Metric(name="time.real_s",
                             value=timing[2],
                             run_id=run.id))
        session.add(s.Metric(name="time.rss",
                             value=timing[3],
                             run_id=run.id))


class MeasureTimeAndMemory(ext.Extension):
    """Wrap a command with time and store the timings in the database."""
    def __call__(self, binary_command, *args, may_wrap=True, **kwargs):
        from benchbuild.utils.cmd import time
        time_tag = "BENCHBUILD: "
        if may_wrap:
            run_cmd = time["-f", time_tag + "%U-%S-%e-%M", binary_command]

        def handle_timing(run_infos):
            """Takes care of the formating for the timing statistics."""
            from benchbuild.utils import schema as s

            session = s.Session()
            for run_info in run_infos:
                LOG.debug("Persisting time for '%s'", run_info)
                if may_wrap:
                    timings = fetch_time_output(
                        time_tag,
                        time_tag + "{:g}-{:g}-{:g}-{:g}",
                        run_info.stderr.split("\n"))
                    if timings:
                        mse_persist_time_and_memory(
                            run_info.db_run, session, timings)
                    else:
                        LOG.warning("No timing information found.")
            session.commit()
            return run_infos

        res = self.call_next(run_cmd, *args, **kwargs)
        return handle_timing(res)


class PollyMSE(RuntimeExperiment):
    """The polly experiment."""

    NAME = "polly-mse"

    def actions_for_project(self, project):
        """Compile & Run the experiment with -O3 enabled."""
        project.cflags = [
            "-O3",
            "-fno-omit-frame-pointer",
            "-mllvm", "-polly",
            "-mllvm", "-polly-enable-mse",
            "-mllvm", "-polly-process-unprofitable",
            "-mllvm", "-polly-enable-optree=0",
            "-mllvm", "-polly-enable-delicm=0",
        ]
        project.compiler_extension = ext.ExtractCompileStats(project, self)
        project.runtime_extension = \
            MeasureTimeAndMemory(
                ext.RuntimeExtension(project, self,
                                     config={
                                         'jobs': int(CFG["jobs"].value())}))

        return self.default_runtime_actions(project)


class PollyMSEReport(Report):
    SUPPORTED_EXPERIMENTS = ["polly-mse"]

    QUERY_EVAL = \
        sa.sql.select([
            sa.column('project_name'),
            sa.column('name'),
            sa.column('bvalue'),
            sa.column('mvalue')
        ]).\
        select_from(
            sa.func.polly_mse_eval(sa.sql.bindparam('exp_ids'))
        )

    def report(self):
        qry = PollyMSEReport.QUERY_EVAL.unique_params(
            exp_ids=self.experiment_ids)
        return self.session.execute(qry).fetchall()

    def generate(self):
        fname = os.path.abspath(self.out_path)
        fname = "{prefix}_mse{ending}".format(
            prefix=os.path.splitext(fname)[0],
            ending=os.path.splitext(fname)[-1])
        res = self.report()
        with open(fname, 'w') as csv_f:
            csv_writer = csv.writer(csv_f)
            csv_writer.writerows([("projct_name", "name", "bvalue", "mvalue")])
            csv_writer.writerows(res)
