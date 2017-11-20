"""
Experiments and evaluation used for IJPP Journal
"""
import copy
import csv
import logging
import os
import uuid
import benchbuild.utils.actions as actions
import benchbuild.extensions as ext
import benchbuild.experiments.polyjit as pj
import benchbuild.reports as reports
import benchbuild.settings as settings
import sqlalchemy as sa


LOG = logging.getLogger(__name__)


class IJPP(pj.PolyJIT):
    """
    Experiments and evaluation used for IJPP Journal

    This experiment compares the following runtime configurations:
        * -O3 'naked' vs. JIT
        * -O3 'inside' vs. JIT
        * -O3 + Polly 'naked' vs. JIT
        * -O3 + Polly 'inside' vs. JIT
    where 'naked' means without any JIT component involved, and 'inside' means
    that the configuration will be executed inside the JIT pipeline, but
    no PolyJIT-features are enabled.
    """

    NAME = "ijpp"

    def actions_for_project(self, project):
        naked_project = copy.deepcopy(project)
        naked_project.run_uuid = uuid.uuid4()

        naked_polly_project = copy.deepcopy(project)
        naked_polly_project.run_uuid = uuid.uuid4()

        project = pj.PolyJIT.init_project(project)
        project.run_uuid = uuid.uuid4()

        jobs = int(settings.CFG["jobs"].value())
        project.cflags += [
            "-mllvm", "-polly-num-threads={0}".format(jobs), "-fopenmp"
        ]
        project.ldflags += [
            "-lgomp"
        ]

        naked_project.cflags += [
            "-O3"
        ]
        naked_polly_project.cflags += [
            "-Xclang", "-load",
            "-Xclang", "LLVMPolly.so",
            "-O3",
            "-mllvm", "-polly",
            "-mllvm", "-polly-parallel",
            "-fopenmp"
        ]

        cfg_jit_inside = {
            "name": "PolyJIT",
            "cores": jobs,
        }

        cfg_jit_inside_opt = {
            "name": "PolyJIT_Opt",
            "cores": jobs,
        }

        cfg_polly_inside = {
            "name": "polly.inside",
            "cores": jobs
        }

        cfg_o3_naked = {
            "name": "o3.naked",
            "cores": jobs
        }

        cfg_polly_naked = {
            "name": "polly.naked",
            "cores": jobs
        }

        # First we configure the "insides"
        pjit_extension = ext.Extension(
            pj.ClearPolyJITConfig(
                ext.LogAdditionals(
                    pj.RegisterPolyJITLogs(
                        pj.EnableJITDatabase(
                            pj.EnablePolyJIT_Opt(
                                ext.RuntimeExtension(
                                    project, self, config=cfg_jit_inside_opt),
                                project=project), project=project)))),
            pj.ClearPolyJITConfig(
                ext.LogAdditionals(
                    pj.RegisterPolyJITLogs(
                        pj.EnableJITDatabase(
                            pj.EnablePolyJIT(
                                ext.RuntimeExtension(
                                    project, self, config=cfg_jit_inside),
                                project=project), project=project)))),
            pj.ClearPolyJITConfig(
                ext.LogAdditionals(
                    pj.RegisterPolyJITLogs(
                        pj.EnableJITDatabase(
                            pj.DisablePolyJIT(
                                ext.RuntimeExtension(
                                    project, self, config=cfg_polly_inside),
                                project=project), project=project))))
        )

        project.runtime_extension = \
            ext.RunWithTime(pjit_extension)
        naked_project.runtime_extension = \
            ext.RunWithTime(
                ext.RuntimeExtension(
                    naked_project, self, config=cfg_o3_naked))
        naked_polly_project.runtime_extension = \
            ext.RunWithTime(
                ext.RuntimeExtension(
                    naked_polly_project, self, config=cfg_polly_naked))

        return [
            actions.Any([
                actions.RequireAll([
                    actions.Echo("Stage: JIT Configurations"),
                    actions.MakeBuildDir(project),
                    actions.Prepare(project),
                    actions.Download(project),
                    actions.Configure(project),
                    actions.Build(project),
                    actions.Run(project),
                    actions.Clean(project),
                    actions.Echo("Stage: JIT Configurations"),
                ]),
                actions.RequireAll([
                    actions.Echo("Stage: O3"),
                    actions.MakeBuildDir(naked_project),
                    actions.Prepare(naked_project),
                    actions.Download(naked_project),
                    actions.Configure(naked_project),
                    actions.Build(naked_project),
                    actions.Run(naked_project),
                    actions.Clean(naked_project),
                    actions.Echo("Stage: O3")
                ]),
                actions.RequireAll([
                    actions.Echo("Stage: O3 Polly"),
                    actions.MakeBuildDir(naked_polly_project),
                    actions.Prepare(naked_polly_project),
                    actions.Download(naked_polly_project),
                    actions.Configure(naked_polly_project),
                    actions.Build(naked_polly_project),
                    actions.Run(naked_polly_project),
                    actions.Clean(naked_polly_project),
                    actions.Echo("Stage: O3 Polly")
                ])
            ])
        ]


class EnableDBExport(pj.PolyJITConfig, ext.Extension):
    """Call the child extensions with an activated PolyJIT."""
    def __call__(self, binary_command, *args, **kwargs):
        ret = None
        with self.argv(PJIT_ARGS=["-polli-optimizer=debug",
                                  "-polli-database-export"]):
            ret = self.call_next(binary_command, *args, **kwargs)
        return ret


class JitExportGeneratedCode(pj.PolyJIT):
    """
    An experiment that executes all projects with PolyJIT support.

    This is our default experiment for speedup measurements.
    """

    NAME = "pj-db-export"

    def actions_for_project(self, project):
        project = pj.PolyJIT.init_project(project)
        project.run_uuid = uuid.uuid4()
        jobs = int(settings.CFG["jobs"].value())
        project.cflags += [
            "-mllvm", "-stats",
            "-mllvm", "-polly-num-threads={0}".format(jobs)]

        project.ldflags += [
            "-lgomp"
        ]

        cfg_with_jit = {
            "name": "PolyJIT",
            "cores": jobs
        }

        cfg_without_jit = {
            "name": "polly.inside",
            "cores": jobs
        }


        jit = ext.RuntimeExtension(project, self, config=cfg_with_jit)
        enable_jit = pj.EnablePolyJIT(jit, project=project)

        no_jit = ext.RuntimeExtension(project, self, config=cfg_without_jit)
        disable_jit = pj.DisablePolyJIT(no_jit, project=project)

        pjit_extension = ext.Extension(
            pj.ClearPolyJITConfig(
                ext.LogAdditionals(
                    pj.RegisterPolyJITLogs(
                        pj.EnableJITDatabase(
                            EnableDBExport(enable_jit),
                            project=project)))),
            pj.ClearPolyJITConfig(
                ext.LogAdditionals(
                    pj.RegisterPolyJITLogs(
                        pj.EnableJITDatabase(
                            EnableDBExport(disable_jit),
                            project=project))))
        )

        project.runtime_extension = ext.RunWithTime(pjit_extension)
        return JitExportGeneratedCode.default_runtime_actions(project)


class IJPPReport(reports.Report):
    SUPPORTED_EXPERIMENTS = ['ijpp']

    QUERY_TIME = \
        sa.sql.select([
            sa.column('project'),
            sa.column('group'),
            sa.column('domain'),
            sa.column('config'),
            sa.column('time'),
            sa.column('variants'),
            sa.column('cachehits')
        ]).select_from(sa.func.ijpp_total_runtime(sa.sql.bindparam('exp_ids')))

    QUERY_REGION = \
        sa.sql.select([
            sa.column('project'),
            sa.column('region'),
            sa.column('config'),
            sa.column('runtime')
        ]).\
        select_from(
            sa.func.ijpp_region_wise(sa.sql.bindparam('exp_ids'))
        )

    def report(self):
        print("I found the following matching experiment ids")
        print("  \n".join([str(x) for x in self.experiment_ids]))

        qry = IJPPReport.QUERY_TIME.unique_params(exp_ids=self.experiment_ids)
        yield ("runtime",
               ('project', 'group', 'domain', 'config', 'time', 'variants',
                'cachehits'),
               self.session.execute(qry).fetchall())

        qry = IJPPReport.QUERY_REGION.unique_params(
            exp_ids=self.experiment_ids)
        yield ("regions",
               ('project', 'region', 'cores', 'runtime'),
               self.session.execute(qry).fetchall())

    def generate(self):
        for name, header, data in self.report():
            fname = os.path.basename(self.out_path)

            fname = "ijpp_{prefix}_{name}{ending}".format(
                prefix=os.path.splitext(fname)[0],
                ending=os.path.splitext(fname)[-1],
                name=name)
            with open(fname, 'w') as csv_out:
                print("Writing '{0}'".format(csv_out.name))
                csv_writer = csv.writer(csv_out)
                csv_writer.writerows([header])
                csv_writer.writerows(data)
