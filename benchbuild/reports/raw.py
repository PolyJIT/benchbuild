import csv
import os
from benchbuild.reports import Report
import benchbuild.utils.schema as schema


Experiment = schema.Experiment
Project = schema.Project
Run = schema.Run
Metrics = schema.Metric
Config = schema.Config


class RawReport(Report):

    SUPPORTED_EXPERIMENTS = ["raw"]

    def report(self):
        exp_ids = [str(exp_id) for exp_id in self.experiment_ids]
        qr = self.session.query(
            Experiment.name,
            Experiment.begin, Experiment.end, Experiment.description,
            Run.experiment_group,
            Run.project_name, Run.status, Run.run_group,
            Metrics.name, Metrics.value,
            Config.name, Config.value)\
            .filter(Run.experiment_group == Experiment.id)\
            .filter(Run.experiment_group.in_(exp_ids))\
            .filter(Run.id == Metrics.run_id)\
            .filter(Run.id == Config.run_id)

        for r in qr:
            yield r

    def generate(self):
        results_f = os.path.abspath(self.out_path)
        with open(results_f, 'w') as csv_f:
            fieldnames = ["exp_name", "exp_begin", "exp_end", "exp_desc",
                          "exp_id", "project", "status", "run_group", "metric",
                          "value", "config", "config_value"]
            csv_w = csv.writer(csv_f)
            csv_w.writerow(fieldnames)
            for rep in self.report():
                csv_w.writerow(rep)