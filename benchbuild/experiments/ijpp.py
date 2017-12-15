"""
Experiments and evaluation used for IJPP Journal
"""
import copy
import csv
import logging
import os
import uuid
import benchbuild.utils.actions as actions
import benchbuild.utils.schedule_tree as st
import benchbuild.experiment as exp
import benchbuild.experiments.polyjit as pj
import benchbuild.extensions as ext
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
        jobs = int(settings.CFG["jobs"].value())
        naked_project = project.clone()
        naked_project.cflags += [
            "-O3"
        ]

        naked_polly_project = project.clone()
        naked_polly_project.cflags += [
            "-Xclang", "-load",
            "-Xclang", "LLVMPolly.so",
            "-O3",
            "-mllvm", "-polly",
            "-mllvm", "-polly-parallel",
            "-fopenmp"
        ]

        project = pj.PolyJIT.init_project(project)
        project.cflags += [
            "-mllvm", "-polly-num-threads={0}".format(jobs), "-fopenmp"
        ]
        project.ldflags += [
            "-lgomp"
        ]

        ext_jit_opt = ext.RuntimeExtension(
            project, self, config={
                "name": "PolyJIT_Opt",
                "cores": jobs,
            }) \
            << pj.EnablePolyJIT_Opt(project=project) \
            << pj.EnableJITDatabase(project=project) \
            << pj.RegisterPolyJITLogs() \
            << pj.ClearPolyJITConfig()

        ext_jit = ext.RuntimeExtension(
            project, self, config={
                "name": "PolyJIT",
                "cores": jobs,
            }) \
            << pj.EnablePolyJIT(project=project) \
            << pj.EnableJITDatabase(project=project) \
            << pj.RegisterPolyJITLogs() \
            << pj.ClearPolyJITConfig()

        ext_jit_polly = ext.RuntimeExtension(
            project, self, config={
                "name": "polly.inside",
                "cores": jobs
            }) \
            << pj.DisablePolyJIT(project=project) \
            << pj.EnableJITDatabase(project=project) \
            << pj.RegisterPolyJITLogs() \
            << pj.ClearPolyJITConfig()

        ext_jit_no_delin = ext.RuntimeExtension(
            project, self, config={
                "name": "PolyJIT.no-delin",
                "cores": jobs
            }) \
            << pj.DisableDelinearization(project=project) \
            << pj.EnablePolyJIT(project=project) \
            << pj.EnableJITDatabase(project=project) \
            << pj.RegisterPolyJITLogs() \
            << pj.ClearPolyJITConfig()

        ext_jit_polly_no_delin = ext.RuntimeExtension(
            project, self, config={
                "name": "polly.inside.no-delin",
                "cores": jobs
            }) \
            << pj.DisableDelinearization(project=project) \
            << pj.DisablePolyJIT(project=project) \
            << pj.EnableJITDatabase(project=project) \
            << pj.RegisterPolyJITLogs() \
            << pj.ClearPolyJITConfig()

        # JIT configurations:
        #   PolyJIT, polly.inside,
        #   PolyJIT_Opt, polly.inside.no-delin
        project.runtime_extension = ext.Extension(
            ext_jit_opt,
            ext_jit,
            ext_jit_polly,
            ext_jit_no_delin,
            ext_jit_polly_no_delin
        ) << ext.RunWithTime()

        # O3
        naked_project.runtime_extension = ext.RuntimeExtension(
            naked_project, self, config={
                "name": "o3.naked",
                "cores": jobs
            }) \
            << ext.RunWithTime()

        # Polly
        naked_polly_project.runtime_extension = ext.RuntimeExtension(
            naked_polly_project, self, config={
                "name": "polly.naked",
                "cores": jobs
            }) \
            << ext.RunWithTime()

        def ijpp_config(_project, name):
            return actions.RequireAll([
                actions.Echo("Stage: JIT Configurations"),
                actions.MakeBuildDir(_project),
                actions.Prepare(_project),
                actions.Download(_project),
                actions.Configure(_project),
                actions.Build(_project),
                actions.Run(_project),
                actions.Clean(_project),
                actions.Echo(name),
            ])

        return [
            actions.Any([
                ijpp_config(project, "Stage: JIT Configurations"),
                ijpp_config(naked_project, "Stage: O3"),
                ijpp_config(naked_polly_project, "Stage: O3 Polly")
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

        enable_jit = ext.RuntimeExtension(
            project, self, config={
                "name": "PolyJIT",
                "cores": jobs
            }) \
            << pj.EnablePolyJIT(project=project) \
            << EnableDBExport() \
            << pj.EnableJITDatabase(project=project) \
            << pj.RegisterPolyJITLogs() \
            << ext.LogAdditionals() \
            << pj.ClearPolyJITConfig()

        disable_jit = ext.RuntimeExtension(
            project, self, config={
                "name": "polly.inside",
                "cores": jobs
            }) \
            << pj.DisablePolyJIT(project=project) \
            << EnableDBExport() \
            << pj.EnableJITDatabase(project=project) \
            << pj.RegisterPolyJITLogs() \
            << ext.LogAdditionals() \
            << pj.ClearPolyJITConfig()


        project.runtime_extension = ext.Extension(
            enable_jit,
            disable_jit
        )

        return JitExportGeneratedCode.default_runtime_actions(project)

class DBReport(reports.Report):
    SUPPORTED_EXPERIMENTS = ['pj-db-export']
    QUERY_CODE = \
        sa.sql.select([
            sa.column('project'),
            sa.column('group'),
            sa.column('function'),
            sa.column('jit_ast'),
            sa.column('jit_schedule'),
            sa.column('jit_stderr'),
            sa.column('polly_ast'),
            sa.column('polly_schedule'),
            sa.column('polly_stderr')
        ]).select_from(sa.func.ijpp_db_export(sa.sql.bindparam('exp_ids')))


    def report(self):
        qry = DBReport.QUERY_CODE.unique_params(exp_ids=self.experiment_ids)
        yield ("codes", self.session.execute(qry).fetchall())

    def generate(self):
        from jinja2 import Environment, PackageLoader
        import parse
        import pprint
        env = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            loader=PackageLoader('benchbuild', 'utils/templates')
        )
        template = env.get_template('ijpp_code_report.html.inc')
        for name, data in self.report():
            fname = os.path.basename(self.out_path)

            def parse_fn_name(fn_name_str):
                return \
                    parse.parse(
                        "{name}_{id:d}_{mod_hash:d}.pjit.scop_{fn_hash:d}",
                        fn_name_str)

            data = [(row[0], row[1], parse_fn_name(row[2]), row[3],
                     st.parse_schedule_tree(row[4]), row[5], row[6],
                     st.parse_schedule_tree(row[7]), row[8]) for row in data]
            fname = "pj-db-export_{prefix}_{name}.html".format(
                prefix=os.path.splitext(fname)[0],
                name=name)
            with open(fname, 'w') as outfile:
                print("Writing '{0}'".format(outfile.name))
                outfile.write(template.render(
                    data=data
                ))

class IJPPReport(reports.Report):
    SUPPORTED_EXPERIMENTS = ['ijpp', "pj-simple"]

    QUERY_TIME = \
        sa.sql.select([
            sa.column('project'),
            sa.column('group'),
            sa.column('domain'),
            sa.column('config'),
            sa.column('time'),
            sa.column('variants'),
            sa.column('cachehits')
        ]).select_from(sa.func.ijpp_total_runtime(sa.sql.bindparam('exp_id')))

    QUERY_REGION = \
        sa.sql.select([
            sa.column('project'),
            sa.column('region'),
            sa.column('config'),
            sa.column('runtime')
        ]).\
        select_from(
            sa.func.ijpp_region_wise(sa.sql.bindparam('exp_id'))
        )

    QUERY_IJPP_TOTAL = \
        sa.sql.select([
            sa.column('project_name'),
            sa.column('project_group'),
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
            sa.func.ijpp_eval(sa.sql.bindparam('exp_id'))
        )

    QUERY_IJPP_REGION = \
        sa.sql.select([
            sa.column('project_name'),
            sa.column('project_group'),
            sa.column('region'),
            sa.column('cores'),
            sa.column('t_polly'),
            sa.column('t_polyjit'),
            sa.column('speedup')
        ]).\
        select_from(
            sa.func.ijpp_region_wise_compare(sa.sql.bindparam('exp_id'))
        )


    def report(self):
        for exp_id in self.experiment_ids:
            qry = IJPPReport.QUERY_TIME.unique_params(exp_id=exp_id)
            yield ("runtime", exp_id,
                ('project', 'group', 'domain', 'config', 'time', 'variants',
                    'cachehits'),
                self.session.execute(qry).fetchall())

            qry = IJPPReport.QUERY_REGION.unique_params(exp_id=exp_id)
            yield ("regions", exp_id,
                ('project', 'region', 'cores', 'runtime'),
                self.session.execute(qry).fetchall())

            qry = IJPPReport.QUERY_IJPP_TOTAL.unique_params(exp_id=exp_id)
            yield ("complete", exp_id,
                ('project', 'group', 'domain',
                 'speedup',
                 'ohcov_0', 'ohcov_1',
                 'dyncov_0', 'dyncov_1',
                 'cachehits_0', 'cachehits_1',
                 'variants_0', 'variants_1',
                 'codegen_0', 'codegen_1',
                 'scops_0', 'scops_1',
                 't_0', 'o_0', 't_1', 'o_1'),
                self.session.execute(qry).fetchall())

            qry = IJPPReport.QUERY_IJPP_REGION.unique_params(exp_id=exp_id)
            yield ("region_compare", exp_id,
                ('project', 'region', 'cores', 'T_Polly', 'T_PolyJIT',
                    'speedup'),
                self.session.execute(qry).fetchall())

    def generate(self):
        for name, exp_id, header, data in self.report():
            fname = os.path.basename(self.out_path)

            fname = "ijpp_{prefix}_{name}_{exp_id}{ending}".format(
                prefix=os.path.splitext(fname)[0],
                ending=os.path.splitext(fname)[-1],
                exp_id=exp_id,
                name=name)
            with open(fname, 'w') as csv_out:
                print("Writing '{0}'".format(csv_out.name))
                csv_writer = csv.writer(csv_out)
                csv_writer.writerows([header])
                csv_writer.writerows(data)
