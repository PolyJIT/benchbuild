from plumbum import cli

import benchbuild.utils.schema as schema
import benchbuild.experiments as e
import benchbuild.reports as r
from benchbuild.cli.main import BenchBuild


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
    def reports(self, reports):
        self.report_names = reports

    @cli.switch(
        ["-E", "--experiment"],
        str,
        list=True,
        help="Specify experiments to run")
    def experiments(self, experiments):
        self.experiment_names = experiments

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

        e.discover()
        r.discover()
        all_reports = r.ReportRegistry.reports

        def generate_reports(reports, experiments=None):
            if not reports:
                print("No reports found. Sorry.")

            for rcls in reports:
                if experiments:
                    for exp in experiments:
                        report = rcls(exp, self._experiment_ids, self._outfile,
                                      schema.Session())
                else:
                    report = rcls(None, self._experiment_ids, self._outfile,
                                  schema.Session())
                report.generate()

        if self.report_names:
            reports = [
                all_reports[name] for name in all_reports
                if name in self.report_names
            ]
            generate_reports(reports, self.experiment_names)
            exit(0)

        if self.experiment_names:
            reports = [
                all_reports[name] for name in all_reports
                if set(all_reports[name].SUPPORTED_EXPERIMENTS) & set(
                    self.experiment_names)
            ]
            generate_reports(reports, self.experiment_names)
            exit(0)
