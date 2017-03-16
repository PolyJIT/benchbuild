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

from functools import partial
from typing import Iterable

#import pandas as pd
#import seaborn as sns
import sqlalchemy as sa
#import sqlalchemy.orm as orm
from plumbum import local

from benchbuild.experiments.polyjit import PolyJIT
from benchbuild.reports import Report
from benchbuild.utils.actions import (Build, Clean, Configure, Download,
                                      MakeBuildDir, Prepare, Run)
from benchbuild.utils.run import RunInfo
from benchbuild.utils.cmd import time
from benchbuild.project import Project
from benchbuild.experiment import Experiment
from benchbuild.settings import Configuration



class Test(PolyJIT):
    """
    An experiment that executes all projects with PolyJIT support.

    This is our default experiment for speedup measurements.
    """

    NAME = "pj-test"

    def actions_for_project(self, p):
        from benchbuild.settings import CFG

        p = PolyJIT.init_project(p)

        actns = []
        p.run_uuid = uuid.uuid4()
        jobs = int(CFG["jobs"].value())
        p.cflags += ["-Rpass-missed=polli*",
                     "-mllvm", "-polly-num-threads={0}".format(jobs)]
        p.runtime_extension = partial(time_polyjit_and_polly,
                                      p, self, CFG, jobs)

        actns.extend([
            MakeBuildDir(p),
            Prepare(p),
            Download(p),
            Configure(p),
            Build(p),
            Run(p),
            Clean(p)
        ])
        return actns


def time_polyjit_and_polly(project: Project,
                           experiment: Experiment,
                           config: Configuration,
                           jobs: int,
                           run_f: str,
                           args: Iterable[str],
                           **kwargs):
    """
    Run the given binary wrapped with time.

    Args:
        project: The benchbuild.project.
        experiment: The benchbuild.experiment.
        config: The benchbuild.settings.config.
        jobs: Number of cores we should use for this execution.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::benchbuild.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
    """
    from benchbuild.utils.run import track_execution, fetch_time_output
    from benchbuild.settings import CFG
    from benchbuild.utils.db import persist_time, persist_config

    CFG.update(config)
    project.name = kwargs.get("project_name", project.name)
    timing_tag = "BB-JIT: "

    may_wrap = kwargs.get("may_wrap", True)

    run_cmd = local[run_f]
    run_cmd = run_cmd[args]
    if may_wrap:
        run_cmd = time["-f", timing_tag + "%U-%S-%e", run_cmd]

    def handle_timing_info(run_info):
        if may_wrap:
            timings = fetch_time_output(
                timing_tag, timing_tag + "{:g}-{:g}-{:g}",
                run_info.stderr.split("\n"))
            if timings:
                persist_time(run_info.db_run, run_info.session, timings)
            else:
                logging.warning("No timing information found.")
        return run_info

    ri_1 = RunInfo()
    ri_2 = RunInfo()
    with track_execution(run_cmd, project, experiment) as run:
        with local.env(OMP_NUM_THREADS=str(jobs),
                       POLLI_LOG_FILE=CFG["slurm"]["extra_log"].value()):
            ri_1 = handle_timing_info(run())
            persist_config(ri_1.db_run, ri_1.session, {
                "cores": str(jobs - 1),
                "cores-config": str(jobs),
                "recompilation": "enabled",
                "specialization": "enabled"})

    with track_execution(run_cmd, project, experiment) as run:
        with local.env(OMP_NUM_THREADS=str(jobs),
                       POLLI_DISABLE_SPECIALIZATION=1,
                       POLLI_LOG_FILE=CFG["slurm"]["extra_log"].value()):
            ri_2 = handle_timing_info(run())
            persist_config(ri_2.db_run, ri_2.session, {
                "cores": str(jobs - 1),
                "cores-config": str(jobs),
                "recompilation": "enabled",
                "specialization": "disabled"})

    return ri_1 + ri_2


class StatusReport(Report):

    SUPPORTED_EXPERIMENTS = ["pj-test", "pj-seq-test", "raw", "pj", "pj-raw"]
    QUERY_STATUS = \
        sa.sql.select([
            sa.column('name'),
            sa.column('_group'),
            sa.column('status'),
            sa.column('runs')
        ]).\
        select_from(
            sa.func.pj_test_status(sa.sql.bindparam('exp_ids'))
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
