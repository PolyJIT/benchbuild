import logging

from benchbuild.plugins import discover
from benchbuild.settings import CFG


def test_discovery(caplog):
    caplog.set_level(logging.DEBUG, logger='benchbuild')
    CFG['plugins']['projects'] = []
    CFG['plugins']['experiments'] = []
    CFG["plugins"]["reports"] = [
        'benchbuild.non_existing', 'benchbuild.reports.raw'
    ]
    discover()

    assert caplog.record_tuples == [
        ('benchbuild.plugins', logging.ERROR,
         "Could not find 'benchbuild.non_existing'"),
        ('benchbuild.plugins', logging.DEBUG,
         "ImportError: No module named 'benchbuild.non_existing'"),
        ('benchbuild.plugins', logging.INFO,
         "Found report: benchbuild.reports.raw"),
    ]
