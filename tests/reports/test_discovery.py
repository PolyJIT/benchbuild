import logging

from benchbuild.plugins import discover
from benchbuild.settings import CFG


def test_discovery(caplog):
    caplog.set_level(logging.DEBUG, logger='benchbuild')
    CFG['plugins']['projects'] = []
    CFG['plugins']['experiments'] = []
    CFG["plugins"]["reports"] = [
        "benchbuild.non.existing", "benchbuild.reports.raw"
    ]
    discover()

    assert caplog.record_tuples == [
        ('benchbuild.plugins', logging.ERROR,
         "Could not find 'benchbuild.non.existing'"),
        ('benchbuild.plugins', logging.DEBUG,
         "Found report: benchbuild.reports.raw"),
    ]
