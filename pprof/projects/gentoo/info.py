"""
Get package infos, e.g., specific ebuilds for given languages, from gentoo chroot.
"""
from pprof.projects.gentoo.portage_gen import Portage_Gen
from pprof.utils.run import run, uchroot
from plumbum import local
from pprof.settings import CFG

class Info(Portage_Gen):
    """
    Info experiment to retrieve package information from portage.
    """

    NAME = "gentoo-info"
    DOMAIN = "debug"

    def build(self):
        with local.cwd(self.builddir):
            with local.env(CC="gcc", CXX="g++"):
                emerge_in_chroot = uchroot()["/usr/bin/emerge"]
                run(emerge_in_chroot["app-portage/portage-utils"])

            qgrep_in_chroot = uchroot()["/usr/bin/qgrep"]
            ebuilds = set()
            for language in CFG["gentoo"]["autotest-lang"].value().split(','):
                output = qgrep_in_chroot("-l", \
                        get_string_for_language(language))
                for line in output.split('\n'):
                    if "ebuild" in line:
                        parts = line.split('.ebuild')[0].split('/')
                        ebuilds.add(parts[0] + '/' + parts[1])

            file_location = CFG["gentoo"]["gentoo-autotest-loc"].value()
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
