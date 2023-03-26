import logging
import typing as tp

import parse

from benchbuild.extensions import base
from benchbuild.settings import CFG
from benchbuild.utils import db
from benchbuild.utils.cmd import time

LOG = logging.getLogger(__name__)


class RunWithTime(base.Extension):
    """Wrap a command with time and store the timings in the database."""

    def __call__(self, binary_command, *args, may_wrap=True, **kwargs):
        time_tag = "BENCHBUILD: "
        if may_wrap:
            run_cmd = time["-f", time_tag + "%U-%S-%e", binary_command]

        def handle_timing(run_infos):
            """Takes care of the formating for the timing statistics."""
            if not CFG["db"]["enabled"]:
                return run_infos

            # pylint: disable=import-outside-toplevel
            from benchbuild.utils import schema as s

            session = s.Session()
            for run_info in run_infos:
                if may_wrap:
                    timings = fetch_time_output(
                        time_tag, time_tag + "{:g}-{:g}-{:g}",
                        run_info.stderr.split("\n")
                    )
                    if timings:
                        db.persist_time(run_info.db_run, session, timings)
                    else:
                        LOG.warning("No timing information found.")
            session.commit()
            return run_infos

        res = self.call_next(run_cmd, *args, **kwargs)
        return handle_timing(res)

    def __str__(self):
        return "Time execution of wrapped binary"


def fetch_time_output(marker: str, format_s: str,
                      ins: tp.List[str]) -> tp.List[parse.Match]:
    """
    Fetch the output /usr/bin/time from a.

    Args:
        marker: The marker that limits the time output
        format_s: The format string used to parse the timings
        ins: A list of lines we look for the output.

    Returns:
        A list of timing tuples
    """
    timings = [x for x in ins if marker in x]
    res = [parse.parse(format_s, t) for t in timings]
    return [_f for _f in res if _f]
