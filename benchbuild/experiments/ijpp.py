"""
Experiments and evaluation used for IJPP Journal
"""
import copy
import logging
import uuid
import benchbuild.utils.actions as actions
import benchbuild.extensions as ext
import benchbuild.experiments.polyjit as pj
import benchbuild.settings as settings

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
            "-mllvm", "-polly-num-threads={0}".format(jobs)]

        naked_project.cflags += [
            "-O3"
        ]
        naked_polly_project.cflags += [
            "-Xclang", "-load",
            "-Xclang", "LLVMPolly.so",
            "-O3",
            "-mllvm", "-polly"
        ]

        cfg_jit_inside = {
            "name": "PolyJIT",
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
            actions.MakeBuildDir(project),
            actions.Prepare(project),
            actions.Download(project),
            actions.Configure(project),
            actions.Build(project),
            actions.Run(project),
            actions.Clean(project),

            actions.MakeBuildDir(naked_project),
            actions.Prepare(naked_project),
            actions.Download(naked_project),
            actions.Configure(naked_project),
            actions.Build(naked_project),
            actions.Run(naked_project),
            actions.Clean(naked_project),

            actions.MakeBuildDir(naked_polly_project),
            actions.Prepare(naked_polly_project),
            actions.Download(naked_polly_project),
            actions.Configure(naked_polly_project),
            actions.Build(naked_polly_project),
            actions.Run(naked_polly_project),
            actions.Clean(naked_polly_project)
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
            "-Rpass-missed=polli*",
            "-mllvm", "-stats",
            "-mllvm", "-polly-num-threads={0}".format(jobs)]

        cfg_with_jit = {
            'jobs': jobs,
            "cflags": project.cflags,
            "cores": str(jobs - 1),
            "cores-config": str(jobs),
            "recompilation": "enabled",
            "specialization": "enabled"
        }

        cfg_without_jit = {
            'jobs': jobs,
            "cflags": project.cflags,
            "cores": str(jobs - 1),
            "cores-config": str(jobs),
            "recompilation": "enabled",
            "specialization": "disabled"
        }

        jit = ext.RuntimeExtension(project, self, config=cfg_with_jit)
        enable_jit = pj.EnablePolyJIT(jit, project=project)

        no_jit = ext.RuntimeExtension(project, self, config=cfg_without_jit)
        disable_jit = pj.EnablePolyJIT(no_jit, project=project)

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

