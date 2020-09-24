"""Subcommand for experiment handling."""
from plumbum import cli

from benchbuild import experiment


class BBExperiment(cli.Application):
    """Manage BenchBuild's known experiments."""

    def main(self, *args: str) -> int:
        del args

        if not self.nested_command:
            self.help()
        return 0


@BBExperiment.subcommand("view")
class BBExperimentView(cli.Application):
    """View available experiments."""

    def main(self, *args: str) -> int:
        del args

        all_exps = experiment.discovered()
        for exp_cls in all_exps.values():
            print(exp_cls.NAME)
            docstring = exp_cls.__doc__ or "-- no docstring --"
            print(("    " + docstring))
        return 0
