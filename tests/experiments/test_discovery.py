import logging

from benchbuild.plugins import discover
from benchbuild.settings import CFG


def test_discovery(caplog):
    caplog.set_level(logging.DEBUG, logger='benchbuild')
    CFG['plugins']['projects'] = []
    CFG['plugins']['reports'] = []
    CFG["plugins"]["experiments"] = [
        "benchbuild.non.existing", "benchbuild.reports.raw"
    ]
    discover()

    assert caplog.record_tuples == [
        ('benchbuild.plugins', logging.ERROR,
         "Could not find 'benchbuild.non.existing'"),
        ('benchbuild.plugins', logging.ERROR,
         "ImportError: No module named 'benchbuild.non'"),
    ]
