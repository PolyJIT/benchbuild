#!/usr/bin/env python3
""" Analyze the BB database. """

from plumbum import cli

from benchbuild.cli.main import BenchBuild


def print_runs(query):
    """ Print all rows in this result query. """

    if query is None:
        return

    for tup in query:
        print(("{0} @ {1} - {2} id: {3} group: {4}".format(
            tup.end, tup.experiment_name, tup.project_name,
            tup.experiment_group, tup.run_group)))


def print_logs(query, types=None):
    """ Print status logs. """
    if query is None:
        return

    for run, log in query:
        print(("{0} @ {1} - {2} id: {3} group: {4} status: {5}".format(
            run.end, run.experiment_name, run.project_name,
            run.experiment_group, run.run_group, log.status)))
        print(("command: {0}".format(run.command)))
        if "stderr" in types:
            print("StdErr:")
            print((log.stderr))
        if "stdout" in types:
            print("StdOut:")
            print((log.stdout))
        print()


@BenchBuild.subcommand("log")
class BenchBuildLog(cli.Application):
    """ Frontend command to the benchbuild database. """

    @cli.switch(["-E", "--experiment"],
                str,
                list=True,
                help="Experiments to fetch the log for.")
    def experiment(self, experiments):
        """ Set the experiments to fetch the log for. """
        self._experiments = experiments

    @cli.switch(["-e", "--experiment-id"],
                str,
                list=True,
                help="Experiment IDs to fetch the log for.")
    def experiment_ids(self, experiment_ids):
        """ Set the experiment ids to fetch the log for. """
        self._experiment_ids = experiment_ids

    @cli.switch(["-p", "--project-id"],
                str,
                list=True,
                help="Project IDs to fetch the log for.")
    def project_ids(self, project_ids):
        """ Set the project ids to fetch the log for. """
        self._project_ids = project_ids

    @cli.switch(["-t", "--type"],
                cli.Set("stdout", "stderr"),
                list=True,
                help="Set the output types to print.")
    def log_type(self, types):
        """ Set the output types to print. """
        self._types = types

    _experiments = None
    _experiment_ids = None
    _project_ids = None
    _types = None

    def main(self, *projects):
        """ Run the log command. """
        from benchbuild.utils.schema import Session, Run, RunLog

        session = Session()

        exps = self._experiments
        exp_ids = self._experiment_ids
        project_ids = self._project_ids
        types = self._types

        if types is not None:
            query = session.query(Run, RunLog).filter(Run.id == RunLog.run_id)
        else:
            query = session.query(Run)

        if exps is not None:
            query = query.filter(Run.experiment_name.in_(exps))

        if exp_ids is not None:
            query = query.filter(Run.experiment_group.in_(exp_ids))

        if projects is not None:
            query = query.filter(Run.project_name.in_(projects))

        if project_ids is not None:
            query = query.filter(Run.run_group.in_(project_ids))

        if types is not None:
            print_logs(query, types)
        else:
            print_runs(query)
