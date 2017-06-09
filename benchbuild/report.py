from plumbum import cli
import benchbuild.reports as Reports
import benchbuild.experiments as Experiments


ReportRegistry = Reports.ReportRegistry


class BenchBuildReport(cli.Application):
    """Generate Reports from the benchbuild db."""

    def __init__(self, executable):
        super(BenchBuildReport, self).__init__(executable=executable)
        self.experiment_names = []
        self._experiment_ids = []
        self._outfile = "report.csv"

    @cli.switch(["-E", "--experiment"], str, list=True,
                help="Specify experiments to run")
    def experiments(self, experiments):
        self.experiment_names = experiments

    @cli.switch(["-e", "--experiment-id"], str, list=True,
                help="Specify an experiment id to run")
    def experiment_ids(self, ids):
        self._experiment_ids = ids

    @cli.switch(["-o", "--outfile"], str,
                help="Output file name")
    def outfile(self, outfile):
        self._outfile = outfile

    def main(self, *args):
        Experiments.discover()
        Reports.discover()
        reports = ReportRegistry.reports

        for exp_name in self.experiment_names:
            if exp_name not in reports:
                print("'{0}' is not a known report.".format(exp_name))
                continue

            for report_cls in reports[exp_name]:
                report = report_cls(exp_name,
                                    self._experiment_ids, self._outfile)
                report.generate()
        exit(0)
