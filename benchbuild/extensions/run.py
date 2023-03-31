import logging
import os

import yaml
from plumbum import local

from benchbuild.extensions import base
from benchbuild.settings import CFG
from benchbuild.utils import db, run
from benchbuild.utils.settings import get_number_of_jobs

LOG = logging.getLogger(__name__)


class RuntimeExtension(base.Extension):
    """
    Default extension to execute and track a binary.

    This can be used for runtime experiments to have a controlled,
    tracked execution of a wrapped binary.
    """

    def __init__(self, project, experiment, *extensions, config=None):
        self.project = project
        self.experiment = experiment

        super().__init__(*extensions, config=config)

    def __call__(self, binary_command, *args, **kwargs):
        self.project.name = kwargs.get("project_name", self.project.name)

        cmd = binary_command[args]
        with run.track_execution(
            cmd, self.project, self.experiment, **kwargs
        ) as _run:
            run_info = _run()
            if self.config:
                run_info.add_payload("config", self.config)
                LOG.info(
                    yaml.dump(
                        self.config,
                        width=40,
                        indent=4,
                        default_flow_style=False
                    )
                )
                self.config['baseline'] = \
                    os.getenv("BB_IS_BASELINE", "False")
                if CFG["db"]["enabled"]:
                    db.persist_config(
                        run_info.db_run, run_info.session, self.config
                    )
        res = self.call_next(binary_command, *args, **kwargs)
        res.append(run_info)
        return res

    def __str__(self):
        return "Run wrapped binary"


class WithTimeout(base.Extension):
    """
    Guard a binary with a timeout.

    This wraps a any binary with a call to `timeout` and sets
    the limit to a given value on extension construction.
    """

    def __init__(self, *extensions, limit="10m", **kwargs):
        super().__init__(*extensions, **kwargs)
        self.limit = limit

    def __call__(self, binary_command, *args, **kwargs):
        # pylint: disable=import-outside-toplevel
        from benchbuild.utils.cmd import timeout
        return self.call_next(
            timeout[self.limit, binary_command], *args, **kwargs
        )


class SetThreadLimit(base.Extension):
    """Sets the OpenMP thread limit, based on your settings.

    This extension uses the 'jobs' settings and controls the environment
    variable OMP_NUM_THREADS.
    """

    def __call__(self, binary_command, *args, **kwargs):
        config = self.config
        if config is not None and 'jobs' in config.keys():
            jobs = get_number_of_jobs(config)
        else:
            LOG.warning("Parameter 'config' was unusable, using defaults")
            jobs = get_number_of_jobs(CFG)

        ret = None
        with local.env(OMP_NUM_THREADS=str(jobs)):
            ret = self.call_next(binary_command, *args, **kwargs)
        return ret

    def __str__(self):
        return "Limit number of OpenMP threads"


class Rerun(base.Extension):
    pass
