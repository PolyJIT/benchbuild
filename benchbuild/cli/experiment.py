"""Subcommand for experiment handling."""
from plumbum import cli
import benchbuild.experiment as exp
import benchbuild.experiments as experiments
from benchbuild.cli.main import BenchBuild


@BenchBuild.subcommand("experiment")
class BBExperiment(cli.Application):
    """Manage BenchBuild's known experiments."""

    def main(self):
        if not self.nested_command:
            self.help()


@BBExperiment.subcommand("view")
class BBExperimentView(cli.Application):
    """View available experiments."""

    def main(self):
        experiments.discover()
        all_exps = exp.ExperimentRegistry.experiments
        for exp_cls in all_exps.values():
            print(exp_cls.NAME)
            docstring = exp_cls.__doc__ or "-- no docstring --"
            print(("    " + docstring))
