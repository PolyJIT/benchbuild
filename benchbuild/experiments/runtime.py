import re

from plumbum import local

from benchbuild.experiment import Experiment


class RuntimeExperiment(Experiment):
    """Additional runtime only features for experiments."""

    def get_papi_calibration(self, calibrate_call):
        """
        Get calibration values for PAPI based measurements.

        Args:
            project (Project):
                Unused (deprecated).
            calibrate_call (benchbuild.utils.cmd):
                The calibration command we will use.
        """
        with local.cwd(self.builddir):
            with local.env(BB_USE_CSV=0, BB_USE_FILE=0):
                calib_out = calibrate_call()

        calib_pattern = re.compile(
            r'Real time per call \(ns\): (?P<val>[0-9]+.[0-9]+)')
        for line in calib_out.split('\n'):
            res = calib_pattern.search(line)
            if res:
                return res.group('val')
        return None

    def persist_calibration(self, project, cmd, calibration):
        """
        Persist the result of a calibration call.

        Args:
            project (benchbuild.Project):
                The calibration values will be assigned to this project.
            cmd (benchbuild.utils.cmd):
                The command we used to generate the calibration values.
            calibration (int):
                The calibration time in nanoseconds.
        """
        if calibration:
            from benchbuild.utils.db import create_run
            from benchbuild.utils import schema as s

            run, session = create_run(
                str(cmd), project.name, self.name, project.run_uuid)
            metric = s.Metric(name="papi.calibration.time_ns",
                              value=calibration,
                              run_id=run.id)
            session.add(metric)
            session.commit()
