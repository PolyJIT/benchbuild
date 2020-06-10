"""
Get package infos, e.g., specific ebuilds for given languages,
from gentoo chroot.
"""
import re

from plumbum import local

from benchbuild.projects.gentoo import autoportage as ap
from benchbuild.settings import CFG
from benchbuild.utils import run, uchroot


class Info(ap.AutoPortage):
    """
    Info experiment to retrieve package information from portage.
    """

    NAME = "info"
    DOMAIN = "debug"

    def compile(self):
        with local.env(CC="gcc", CXX="g++"):
            emerge_in_chroot = uchroot.uchroot()["/usr/bin/emerge"]
            _emerge_in_chroot = run.watch(emerge_in_chroot)
            _emerge_in_chroot("app-portage/portage-utils")
            _emerge_in_chroot("app-portage/gentoolkit")

        qgrep_in_chroot = uchroot.uchroot()["/usr/bin/qgrep"]
        equery_in_chroot = uchroot.uchroot()["/usr/bin/equery"]

        ebuilds = set()

        languages = CFG["gentoo"]["autotest_lang"].value
        use_flags = CFG["gentoo"]["autotest_use"].value
        file_location = str(CFG["gentoo"]["autotest_loc"])

        for language in languages:
            output = qgrep_in_chroot("-l", get_string_for_language(language))
            for line in output.split('\n'):
                if "ebuild" in line:
                    parts = line.split('.ebuild')[0].split('/')
                    package_atom = '{0}/{1}'.format(parts[0], parts[1])
                    ebuilds.add(package_atom)

        for use in use_flags:
            output = equery_in_chroot("-q", "hasuse", "-p", use)
            ebuilds_use = set()
            for line in output.split('\n'):
                ebuilds_use.add(re.sub(r"(.*)-[0-9]+.*$", r"\1", line))

            ebuilds = ebuilds.intersection(ebuilds_use)

        with open(file_location, "w") as output_file:
            for ebuild in sorted(ebuilds):
                output_file.write(str(ebuild) + "\n")
            output_file.flush()


def get_string_for_language(language_name):
    """
    Maps language names to the corresponding string for qgrep.
    """
    language_name = language_name.lower().lstrip()
    if language_name == "c":
        return "tc-getCC"
    if language_name in ('c++', 'cxx'):
        return "tc-getCXX"
    return language_name
