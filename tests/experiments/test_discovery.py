import logging

from benchbuild.experiment import ExperimentRegistry
from benchbuild.experiments import discover
from benchbuild.settings import CFG


def test_discovery(caplog):
    caplog.set_level(logging.DEBUG, logger='benchbuild')
    CFG['plugins']['experiments'] = [
        "benchbuild.non.existing", "benchbuild.reports.raw"
    ]

    discover()
    assert caplog.record_tuples == [
        ('benchbuild.experiments', logging.ERROR,
         "Could not find 'benchbuild.non.existing'"),
        ('benchbuild.experiments', logging.ERROR,
         "ImportError: No module named 'benchbuild.non'"),
    ]

    default = CFG['plugins']['experiments'].node['default']
    CFG['plugins']['experiments'] = default

    discover()
