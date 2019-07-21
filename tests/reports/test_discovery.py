import logging

from benchbuild.reports import discover
from benchbuild.settings import CFG


def test_discovery(caplog):
    caplog.set_level(logging.DEBUG, logger='benchbuild')
    CFG["plugins"]["reports"] = [
        "benchbuild.non.existing", "benchbuild.reports.raw"
    ]
    discover()

    assert caplog.record_tuples == [
        ('benchbuild.reports', logging.ERROR,
         "Could not find 'benchbuild.non.existing'"),
        ('benchbuild.reports', logging.DEBUG,
         "Found report: benchbuild.reports.raw"),
    ]
