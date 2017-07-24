"""
The 'pollytest' experiment.

This experiment uses four different configs to analyse the compilestats' and the
time's behavior regarding the position of polly and unprofitable processes.
"""
import copy
import logging
import os
import uuid
import pandas as pd

import sqlalchemy as sa
import benchbuild.experiment as exp
import benchbuild.extensions as ext
import benchbuild.reports as report


LOG = logging.getLogger(__name__)


class PollyTest(exp.Experiment):
    """
    An experiment that executes projects with different configurations.

    The time and the compilestats are collected.
    """
    NAME = "pollytest"

    def actions_for_project(self, project):
        actns = []
        project.cflags = ["-Xclang", "-load", "-Xclang", "LLVMPolly.so"]

        newp = copy.deepcopy(project)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + ["-O3"]
        cfg = {
            "name": "-O3"
        }
        newp.compiler_extension = \
            ext.ExtractCompileStats(newp, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))

        newp = copy.deepcopy(project)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + ["-O3", "-mllvm", "-polly"]
        cfg = {
            "name": "-O3 -polly"
        }
        newp.compiler_extension = \
            ext.ExtractCompileStats(newp, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))

        newp = copy.deepcopy(project)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + [
           "-O3", "-mllvm",
           "-polly", "-mllvm",
           "-polly-position=before-vectorizer"]
        cfg = {
            "name": "-O3 -polly -polly-position=before-vectorizer"
        }
        newp.compiler_extension = \
            ext.ExtractCompileStats(newp, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))

        newp = copy.deepcopy(project)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + [
           "-O3", "-mllvm",
           "-polly", "-mllvm",
           "-polly-process-unprofitable",
           "-mllvm", "-polly-position=before-vectorizer"]
        cfg = {
            "name": "-O3 -polly -polly-position=before-vectorizer "
                    "-polly-process-unprofitable"
        }
        newp.compiler_extension = \
            ext.ExtractCompileStats(newp, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))

        newp = copy.deepcopy(project)
        newp.run_uuid = uuid.uuid4()
        newp.cflags = newp.cflags + [
           "-O3", "-mllvm",
           "-polly", "-mllvm",
           "-polly-process-unprofitable"]
        cfg = {
            "name": "-O3 -polly -polly-process-unprofitable"
        }
        newp.compiler_extension = \
            ext.ExtractCompileStats(newp, self, config=cfg)
        actns.extend(self.default_compiletime_actions(newp))
        return actns


class PollyTestReport(report.Report):
    SUPPORTED_EXPERIMENTS = ["pollytest"]
    QUERY_EVAL = \
        sa.sql.select([
        ]).\
        select_from(
            sa.func.pollytest_eval(
                sa.sql.bindparam('exp_ids'),
                sa.sql.bindparam('components')))

    def report(self):
        print("I found the following matching experiment ids")
        print("  \n".join([str(x) for x in self.experiment_ids]))

        qry = PollyTestReport.\
            QUERY_EVAL.unique_params(
                exp_ids=self.experiment_ids,
                components=["polly-scops", "polly-detect", "polly"]
            )

        df = pd.read_sql_query(qry, self.session.bind)
        print(df.head())

        return df

    def generate(self):
        fname = os.path.basename(self.out_path)
        fname = "{prefix}_pollytest{ending}".format(
            prefix=os.path.splitext(fname)[0],
            ending=os.path.splitext(fname)[-1])
        self.report()
