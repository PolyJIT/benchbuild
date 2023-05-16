import logging
import typing as tp
from typing import TYPE_CHECKING

import yaml
from plumbum.commands.base import BoundCommand

from benchbuild.extensions import base
from benchbuild.settings import CFG
from benchbuild.utils import db, run

if TYPE_CHECKING:
    from benchbuild.experiment import Experiment
    from benchbuild.project import Project

LOG = logging.getLogger(__name__)


class RunCompiler(base.Extension):
    """Default extension for compiler execution.

    This extension silences a few warnings, e.g., unused-arguments and
    handles database tracking for compiler commands. It is used as the default
    action for compiler execution.
    """

    def __init__(
        self,
        project: 'Project',
        experiment: 'Experiment',
        *extensions: base.Extension,
        config: tp.Optional[tp.Dict[str, str]] = None
    ):
        self.project = project
        self.experiment = experiment

        super().__init__(*extensions, config=config)

    def __call__(
        self,
        command: BoundCommand,
        *args: str,
        project: tp.Optional['Project'] = None,
        rerun_on_error: bool = True,
        **kwargs: tp.Any
    ) -> tp.List[run.RunInfo]:
        if project:
            self.project = project

        original_command = command[args]
        new_command = command["-Qunused-arguments"]
        new_command = new_command[args]
        new_command = new_command[self.project.cflags]
        new_command = new_command[self.project.ldflags]

        with run.track_execution(
            new_command, self.project, self.experiment, **kwargs
        ) as _run:
            run_info = _run()
            if self.config:
                LOG.info(
                    yaml.dump(
                        self.config,
                        width=40,
                        indent=4,
                        default_flow_style=False
                    )
                )
                if CFG["db"]["enabled"]:
                    db.persist_config(
                        run_info.db_run, run_info.session, self.config
                    )

            if run_info.has_failed:
                with run.track_execution(
                    original_command, self.project, self.experiment, **kwargs
                ) as _run:
                    LOG.warning("Fallback to: %s", str(original_command))
                    run_info = _run()

        res = self.call_next(new_command, *args, **kwargs)
        res.append(run_info)
        return res

    def __str__(self):
        return "Compile /w fallback"
