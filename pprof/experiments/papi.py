"""
PAPI based experiments.

These types of experiments (papi & papi-std) need to instrument the
project with libpprof support to work.

"""
from pprof.experiment import (RuntimeExperiment, step, substep)
from pprof.utils.run import partial
from pprof.experiments.raw import run_with_time
from plumbum import local
from os import path


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
