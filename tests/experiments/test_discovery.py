import logging

from benchbuild.plugins import discover
from benchbuild.settings import CFG


def test_discovery(caplog):
    caplog.set_level(logging.DEBUG, logger='benchbuild')
    CFG['plugins']['projects'] = []
    CFG['plugins']['reports'] = []
    CFG["plugins"]["experiments"] = ["benchbuild.non_existing"]
    discover()
    assert caplog.record_tuples == [
        ('benchbuild.plugins', logging.ERROR,
         "Could not find 'benchbuild.non_existing'"),
        ('benchbuild.plugins', logging.DEBUG,
         "ImportError: No module named 'benchbuild.non_existing'"),
    ]

    def_exps = CFG['plugins']['experiments'].node['default']
    CFG['plugins']['experiments'] = def_exps

    def_prjs = CFG['plugins']['projects'].node['default']
    CFG['plugins']['projects'] = def_prjs

    def_reports = CFG['plugins']['reports'].node['default']
    CFG['plugins']['reports'] = def_reports

    discover()
