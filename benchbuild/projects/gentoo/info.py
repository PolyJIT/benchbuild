"""
Get package infos, e.g., specific ebuilds for given languages,
from gentoo chroot.
"""
from benchbuild.projects.gentoo import autoportage as ap
from benchbuild.utils.run import run, uchroot
from plumbum import local
from benchbuild.settings import CFG
import re


class Info(ap.AutoPortage):
    """
    Info experiment to retrieve package information from portage.
    """

    NAME = "gentoo-info"
    DOMAIN = "debug"

    def build(self):
        with local.env(CC="gcc", CXX="g++"):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            run(emerge_in_chroot["app-portage/portage-utils"])
            run(emerge_in_chroot["app-portage/gentoolkit"])

        qgrep_in_chroot = uchroot()["/usr/bin/qgrep"]
        ebuilds = set()
        for language in CFG["gentoo"]["autotest_lang"].value().split(','):
            output = qgrep_in_chroot("-l", \
                    get_string_for_language(language))
            for line in output.split('\n'):
                if "ebuild" in line:
                    parts = line.split('.ebuild')[0].split('/')
                    ebuilds.add(parts[0] + '/' + parts[1])

        use_flags = CFG["gentoo"]["autotest_use"].value().split(' ')
        for use in use_flags:
            if use == "":
                continue
            equery_in_chroot = uchroot()["/usr/bin/equery"]
            output = equery_in_chroot("-q", "hasuse", "-p", use)
            ebuilds_use = set()
            for line in output.split('\n'):
                ebuilds_use.add(re.sub(r"(.*)-[0-9]+.*$", r"\1", line))

            ebuilds = ebuilds.intersection(ebuilds_use)

        file_location = CFG["gentoo"]["autotest_loc"].value()
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
    if language_name == "c++" or language_name == "cxx":
        return "tc-getCXX"
    if language_name == "":
        return ""
