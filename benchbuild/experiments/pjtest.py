"""
A test experiment for PolyJIT.

This experiment should only be used to test various features of PolyJIT. It
provides only 1 configuration (maximum number of cores) and tests 2 run-time
execution profiles of PolyJIT:
  1) PolyJIT enabled, with specialization
  2) PolyJIT enabled, without specialization
"""
import uuid
import csv
from functools import partial

from plumbum import local

from benchbuild.utils.actions import (Build, Clean, Configure, Download,
                                      MakeBuildDir, Prepare, Run)
from benchbuild.utils.cmd import time
from benchbuild.experiments.polyjit import PolyJIT
from benchbuild.reports import Report

import sqlalchemy as sa

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
        p.cflags += ["-mllvm", "-polly-num-threads={0}".format(jobs)]
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


def time_polyjit_and_polly(project, experiment, config, jobs, run_f, args,
                           **kwargs):
    """
    Run the given binary wrapped with time.

    Args:
        project: The benchbuild.project.
        experiment: The benchbuild.experiment.
        config: The benchbuild.settings.config.
        jobs: Number of cores we should use for this exection.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::benchbuild.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
    """
    from benchbuild.utils.run import guarded_exec, fetch_time_output
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

    def handle_timing_info(ri):
        if may_wrap:
            timings = fetch_time_output(
                timing_tag, timing_tag + "{:g}-{:g}-{:g}",
                ri.stderr.split("\n"))
            if timings:
                persist_time(ri.db_run, ri.session, timings)
        return ri

    with local.env(OMP_NUM_THREADS=str(jobs),
                   POLLI_LOG_FILE=CFG["slurm"]["extra_log"].value()):
        with guarded_exec(run_cmd, project, experiment) as run:
            ri = handle_timing_info(run())
    persist_config(ri.db_run, ri.session, {"cores": str(jobs - 1),
                                           "cores-config": str(jobs),
                                           "recompilation": "enabled",
                                           "specialization": "enabled"})

    with local.env(OMP_NUM_THREADS=str(jobs),
                   POLLI_DISABLE_SPECIALIZATION=1,
                   POLLI_LOG_FILE=CFG["slurm"]["extra_log"].value()):
        with guarded_exec(run_cmd, project, experiment) as run:
            ri = handle_timing_info(run())
    persist_config(ri.db_run, ri.session, {"cores": str(jobs - 1),
                                           "cores-config": str(jobs),
                                           "recompilation": "enabled",
                                           "specialization": "disabled"})
    return ri


class TestReport(Report):

    SUPPORTED_EXPERIMENTS = ["pj-test"]

    def report(self):
        func = sa.func
        column = sa.column
        select = sa.sql.select
        bindparam = sa.sql.bindparam

        exps = select([
            column('project'),
            column('total'),
            column('scops'),
            column('overhead'),
            column('ohcov_0'),
            column('ohcov_1'),
            column('dyncov'),
            column('cachehits'),
            column('variants'),
            column('t_0'),
            column('t_1'),
            column('o_1')]).\
            select_from(
                func.pj_test_total_dyncov(bindparam('exp_ids'))
            )

        r1 = self.session.execute(
            exps.unique_params(
                exp_ids=[uuid.UUID(v) for v in self.experiment_ids])
        )
        return r1.fetchall()

    def generate(self):
        report = self.report()
        print("Report has: {0} result rows".format(len(report)))
        with open(self.out_path, 'w') as csv_out:
            csv_writer = csv.writer(csv_out)
            csv_writer.writerows([
                ('project', 'total', 'scops', 'overhead', 'ohcov_0', 'ohcov_1',
                 'dyncov', 'cachehits', 'variants', 't_0', 't_1', 'o_1')
            ])
            csv_writer.writerows(report)


    def __init__(self, exp_ids, outfile):
        super(TestReport, self).__init__(exp_ids, outfile)
