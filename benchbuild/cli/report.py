from plumbum import cli

from benchbuild import experiments, reports
from benchbuild.cli.main import BenchBuild
from benchbuild.utils import schema


@BenchBuild.subcommand("report")
class BenchBuildReport(cli.Application):
    """Generate Reports from the benchbuild db."""

    def __init__(self, executable):
        super(BenchBuildReport, self).__init__(executable=executable)
        self.experiment_names = []
        self.report_names = None
        self._experiment_ids = []
        self._outfile = "report.csv"

    @cli.switch(
        ["-R", "--report"],
        str,
        list=True,
        help="Specify the reports to generate")
    def reports(self, _reports):
        self.report_names = _reports

    @cli.switch(
        ["-E", "--experiment"],
        str,
        list=True,
        help="Specify experiments to run")
    def experiments(self, _experiments):
        self.experiment_names = _experiments

    @cli.switch(
        ["-e", "--experiment-id"],
        str,
        list=True,
        help="Specify an experiment id to run")
    def experiment_ids(self, ids):
        self._experiment_ids = ids

    @cli.switch(["-o", "--outfile"], str, help="Output file name")
    def outfile(self, outfile):
        self._outfile = outfile

    def main(self, *args):
        del args  # Unused

        experiments.discover()
        reports.discover()
        all_reports = reports.ReportRegistry.reports

        def generate_reports(_reports, _experiments=None):
            if not reports:
                print("No reports found. Sorry.")

            for rcls in _reports:
                if _experiments:
                    for exp in _experiments:
                        report = rcls(exp, self._experiment_ids, self._outfile,
                                      schema.Session())
                else:
                    report = rcls(None, self._experiment_ids, self._outfile,
                                  schema.Session())
                report.generate()

        if self.report_names:
            _reports = [
                all_reports[name] for name in all_reports
                if name in self.report_names
            ]
            generate_reports(_reports, self.experiment_names)
            exit(0)

        if self.experiment_names:
            _reports = [
                all_reports[name] for name in all_reports
                if set(all_reports[name].SUPPORTED_EXPERIMENTS) & set(
                    self.experiment_names)
            ]
            generate_reports(_reports, self.experiment_names)
            exit(0)
