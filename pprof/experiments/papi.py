"""
PAPI based experiments.

These types of experiments (papi & papi-std) need to instrument the
project with libpprof support to work.

"""
from pprof.experiment import (RuntimeExperiment, step, substep)
from pprof.experiments.raw import run_with_time
from pprof.utils.run import partial
from plumbum import local
from os import path


def get_compilestats(prog_out):
    """ Get the LLVM compilation stats from :prog_out:. """
    from parse import compile

    stats_pattern = compile("{value:d} {component} - {desc}\n")

    for line in prog_out.split("\n"):
        res = stats_pattern.search(line + "\n")
        if res is not None:
            yield res

def collect_compilestats(project, experiment, config, clang, **kwargs):
    """Collect compilestats."""
    from pprof.utils import run as r
    from pprof.settings import config as c
    from pprof.utils.db import persist_compilestats
    from pprof.utils.run import handle_stdin
    from pprof.utils.schema import CompileStat

    c.update(config)
    clang = handle_stdin(clang["-mllvm", "-stats"], kwargs)

    run, session, retcode, _, stderr = \
        r.guarded_exec(clang, project.name, experiment.name, project.run_uuid)

    if retcode == 0:
        stats = []
        for stat in get_compilestats(stderr):
            compile_s = CompileStat()
            compile_s.name = stat["desc"].rstrip()
            compile_s.component = stat["component"].rstrip()
            compile_s.value = stat["value"]
            stats.append(compile_s)
        persist_compilestats(run, session, stats)


class PapiScopCoverage(RuntimeExperiment):
    """PAPI-based dynamic SCoP coverage measurement."""

    NAME = "papi"

    def run(self):
        """Do the postprocessing, after all projects are done."""
        super(PapiScopCoverage, self).run()
        from pprof.settings import config
        bin_path = path.join(config["llvmdir"], "bin")
        pprof_analyze = local[path.join(bin_path, "pprof-analyze")]

        with local.env(PPROF_EXPERIMENT_ID=str(config["experiment"]),
                       PPROF_EXPERIMENT=self.name,
                       PPROF_USE_DATABASE=1,
                       PPROF_USE_FILE=0,
                       PPROF_USE_CSV=0):
            pprof_analyze()

    def run_project(self, p):
        """
        Create & Run a papi-instrumented version of the project.

        This experiment uses the -jitable flag of libPolyJIT to generate
        dynamic SCoP coverage.
        """
        from pprof.settings import config
        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("Class: Dynamic, PAPI"):
            p.download()
            p.ldflags = ["-L" + llvm_libs, "-lpjit", "-lpprof", "-lpapi"]

            ld_lib_path = [_f
                           for _f in config["ld_library_path"].split(":")
                           if _f]
            p.ldflags = ["-L" + el for el in ld_lib_path] + p.ldflags
            p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli", "-mllvm", "-jitable", "-mllvm",
                        "-instrument", "-mllvm", "-no-recompilation", "-mllvm",
                        "-polly-detect-keep-going"]
            with substep("reconf & rebuild"):
                with local.env(PPROF_ENABLE=0):
                    p.compiler_extension = partial(collect_compilestats, p,
                                                   self, config)
                    p.configure()
                    p.build()
            with substep("run"):
                p.run(partial(run_with_time, p, self, config, 1))

        with step("Evaluation"):
            bin_path = path.join(config["llvmdir"], "bin")
            pprof_calibrate = local[path.join(bin_path, "pprof-calibrate")]
            papi_calibration = self.get_papi_calibration(p, pprof_calibrate)

            self.persist_calibration(p, pprof_calibrate, papi_calibration)


class PapiStandardScopCoverage(PapiScopCoverage):
    """PAPI Scop Coverage, without JIT."""

    NAME = "papi-std"

    def run_project(self, p):
        """
        Create & Run a papi-instrumented version of the project.

        This experiment does not use the -jitable flag of libPolyJIT.
        Therefore, we get the static (aka Standard) SCoP coverage.
        """
        from pprof.settings import config
        llvm_libs = path.join(config["llvmdir"], "lib")

        with step("Class: Standard - PAPI"):
            p.download()
            p.ldflags = ["-L" + llvm_libs, "-lpjit", "-lpprof", "-lpapi"]

            ld_lib_path = [_f
                           for _f in config["ld_library_path"].split(":")
                           if _f]
            p.ldflags = ["-L" + el for el in ld_lib_path] + p.ldflags
            p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolyJIT.so",
                        "-mllvm", "-polli", "-mllvm", "-instrument", "-mllvm",
                        "-no-recompilation", "-mllvm",
                        "-polly-detect-keep-going"]
            with substep("reconf & rebuild"):
                with local.env(PPROF_ENABLE=0):
                    p.configure()
                    p.build()
            with substep("run"):
                p.run(partial(run_with_time, p, self, config, 1))

        with step("Evaluation"):
            bin_path = path.join(config["llvmdir"], "bin")
            pprof_calibrate = local[path.join(bin_path, "pprof-calibrate")]
            papi_calibration = self.get_papi_calibration(p, pprof_calibrate)
            self.persist_calibration(p, pprof_calibrate, papi_calibration)
