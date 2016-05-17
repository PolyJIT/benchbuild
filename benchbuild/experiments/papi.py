"""
PAPI based experiments.

These types of experiments (papi & papi-std) need to instrument the
project with libbenchbuild support to work.

"""
from os import path
from benchbuild.experiment import RuntimeExperiment
from benchbuild.experiments.raw import run_with_time
from benchbuild.utils.run import partial
from benchbuild.utils.actions import (Step, Prepare, Build, Download, Configure, Clean,
                                 MakeBuildDir, Run, Echo)
from benchbuild.settings import CFG
from plumbum import local


def get_compilestats(prog_out):
    """ Get the LLVM compilation stats from :prog_out:. """
    from parse import compile as c

    stats_pattern = c("{value:d} {component} - {desc}\n")

    for line in prog_out.split("\n"):
        res = stats_pattern.search(line + "\n")
        if res is not None:
            yield res

def collect_compilestats(project, experiment, clang, **kwargs):
    """Collect compilestats."""
    from benchbuild.utils.run import guarded_exec, handle_stdin
    from benchbuild.utils.db import persist_compilestats
    from benchbuild.utils.schema import CompileStat

    clang = handle_stdin(clang["-mllvm", "-stats"], kwargs)

    with guarded_exec(clang, project, experiment) as run:
        ri = run()

    if ri.retcode == 0:
        stats = []
        for stat in get_compilestats(ri.stderr):
            compile_s = CompileStat()
            compile_s.name = stat["desc"].rstrip()
            compile_s.component = stat["component"].rstrip()
            compile_s.value = stat["value"]
            stats.append(compile_s)
        persist_compilestats(ri.db_run, ri.session, stats)


class PapiScopCoverage(RuntimeExperiment):
    """PAPI-based dynamic SCoP coverage measurement."""

    NAME = "papi"

    def run(self):
        """Do the postprocessing, after all projects are done."""
        super(PapiScopCoverage, self).run()
        bin_path = path.join(str(CFG["llvm"]["dir"]), "bin")
        benchbuild_analyze = local[path.join(bin_path, "benchbuild-analyze")]

        with local.env(BB_EXPERIMENT_ID=str(CFG["experiment_id"]),
                       BB_EXPERIMENT=self.name,
                       BB_USE_DATABASE=1,
                       BB_USE_FILE=0,
                       BB_USE_CSV=0):
            benchbuild_analyze()

    def actions_for_project(self, p):
        """
        Create & Run a papi-instrumented version of the project.

        This experiment uses the -jitable flag of libPolyJIT to generate
        dynamic SCoP coverage.
        """
        llvm_libs = path.join(str(CFG["llvm"]["dir"].value()), "lib")
        p.ldflags = ["-L" + llvm_libs, "-lpjit", "-lbenchbuild", "-lpapi"]
        ld_lib_path = [_f
                       for _f in CFG["ld_library_path"].value().split(":")
                       if _f]
        p.ldflags = ["-L" + el for el in ld_lib_path] + p.ldflags
        p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                    "-mllvm", "-polli", "-mllvm", "-jitable", "-mllvm",
                    "-instrument", "-mllvm", "-no-recompilation", "-mllvm",
                    "-polly-detect-keep-going"]
        p.compiler_extension = partial(collect_compilestats, p, self)
        p.runtime_extension = partial(run_with_time, p, self, CFG, 1)

        def evaluate_calibration(e):
            bin_path = path.join(str(CFG["llvm"]["dir"]), "bin")
            benchbuild_calibrate = local[path.join(bin_path, "benchbuild-calibrate")]
            papi_calibration = e.get_papi_calibration(p, benchbuild_calibrate)
            e.persist_calibration(p, benchbuild_calibrate, papi_calibration)

        actns = [
            MakeBuildDir(p),
            Echo("{0}: Compiling... {1}".format(self.name, p.name)),
            Prepare(p),
            Download(p),
            Configure(p),
            Build(p),
            Echo("{0}: Running... {1}".format(self.name, p.name)),
            Run(p),
            Clean(p),
            Echo("{0}: Calibrating... {1}".format(self.name, p.name)),
            Step(p, action_fn=partial(evaluate_calibration, self))
        ]
        return actns


class PapiStandardScopCoverage(PapiScopCoverage):
    """PAPI Scop Coverage, without JIT."""

    NAME = "papi-std"

    def actions_for_project(self, p):
        """
        Create & Run a papi-instrumented version of the project.

        This experiment uses the -jitable flag of libPolyJIT to generate
        dynamic SCoP coverage.
        """
        llvm_libs = path.join(str(CFG["llvm"]["dir"].value()), "lib")
        p.ldflags = ["-L" + llvm_libs, "-lpjit", "-lbenchbuild", "-lpapi"]
        ld_lib_path = [_f
                       for _f in CFG["ld_library_path"].value().split(":")
                       if _f]
        p.ldflags = ["-L" + el for el in ld_lib_path] + p.ldflags
        p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                    "-mllvm", "-polli", "-mllvm", "-instrument", "-mllvm",
                    "-no-recompilation", "-mllvm",
                    "-polly-detect-keep-going"]
        p.compiler_extension = partial(collect_compilestats, p, self)
        p.runtime_extension = partial(run_with_time, p, self, CFG, 1)

        def evaluate_calibration(e):
            bin_path = path.join(str(CFG["llvm"]["dir"]), "bin")
            benchbuild_calibrate = local[path.join(bin_path, "benchbuild-calibrate")]
            papi_calibration = e.get_papi_calibration(p, benchbuild_calibrate)
            e.persist_calibration(p, benchbuild_calibrate, papi_calibration)

        actns = [
            MakeBuildDir(p),
            Echo("{0}: Compiling... {1}".format(self.name, p.name)),
            Prepare(p),
            Download(p),
            Configure(p),
            Build(p),
            Echo("{0}: Running... {1}".format(self.name, p.name)),
            Run(p),
            Clean(p),
            Echo("{0}: Calibrating... {1}".format(self.name, p.name)),
            Step(p, action_fn=partial(evaluate_calibration, self))
        ]
        return actns
