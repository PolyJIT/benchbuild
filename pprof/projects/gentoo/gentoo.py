"""
The Gentoo module for running tests on builds from the portage tree.

This will install a stage3 image of gentoo together with a recent snapshot
of the portage tree. For building / executing arbitrary projects successfully it
is necessary to keep the installed image as close to the host system as
possible.
In order to speed up your experience, you can replace the stage3 image that
we pull from the distfiles mirror with a new image that contains all necessary
dependencies for your experiments. Make sure you update the hash alongside
the gentoo image in pprof's source directory.

The following packages are required to run GentooGroup:
    * fakeroot
"""

from pprof.project import Project, ProjectFactory
from plumbum import local


def latest_src_uri():
    """
    Get the latest src_uri for a stage 3 tarball.

    Returns (str):
        Latest src_uri from gentoo's distfiles mirror.
    """
    from plumbum.cmd import curl, cut, tail
    from plumbum import ProcessExecutionError
    from logging import error

    latest_txt = "http://distfiles.gentoo.org/releases/amd64/autobuilds/"\
            "latest-stage3-amd64.txt"
    try:
        src_uri = (curl[latest_txt] | tail["-n", "+3"]
                   | cut["-f1", "-d "])().strip()
    except ProcessExecutionError as proc_ex:
        src_uri = "NOT-FOUND"
        error("Could not determine latest stage3 src uri: {0}", str(proc_ex))
    return src_uri


class GentooGroup(Project):
    """
    Gentoo ProjectGroup is the base class for every portage build.
    """

    def __init__(self, exp, name):
        super(GentooGroup, self).__init__(exp, name, "gentoo", "gentoo")

    src_dir = "gentoo"
    src_file = src_dir + ".tar.bz2"
    src_uri = "http://distfiles.gentoo.org/releases/amd64/autobuilds/{0}" \
        .format(latest_src_uri())

    # download location for portage files
    src_uri_portage = "ftp://sunsite.informatik.rwth-aachen.de/pub/Linux/"\
                    "gentoo/snapshots/portage-latest.tar.bz2"
    src_file_portage = "portage_snap.tar.bz2"

    def download(self):
        from pprof.utils.downloader import Wget
        from pprof.utils.run import run
        from pprof.settings import config
        from plumbum.cmd import cp, tar, fakeroot, rm
        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)

            cp(config["sourcedir"] + "/bin/uchroot", "uchroot")
            run(fakeroot["tar", "xfj", self.src_file])
            rm(self.src_file)
            with local.cwd(self.builddir + "/usr"):
                Wget(self.src_uri_portage, self.src_file_portage)
                run(tar["xfj", self.src_file_portage])
                rm(self.src_file_portage)

    def configure(self):
        from plumbum.cmd import mkdir, cp
        with local.cwd(self.builddir):
            with open("etc/portage/make.conf", 'w') as makeconf:
                lines = '''
# These settings were set by the catalyst build script that automatically
# built this stage.
# Please consult /usr/share/portage/config/make.conf.example for a more
# detailed example.
CFLAGS="-O2 -pipe"
CXXFLAGS="${CFLAGS}"

FEATURES="-sandbox -usersandbox fakeroot -usersync -xattr"

# set compiler
CC="/llvm/bin/clang"
CXX="/llvm/bin/clang++"

PORTAGE_USERNAME = "root"
PORTAGE_GRPNAME = "root"
PORTAGE_INST_GID = 0
PORTAGE_INST_UID = 0

LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/llvm/lib"

# WARNING: Changing your CHOST is not something that should be done lightly.
# Please consult http://www.gentoo.org/doc/en/change-chost.xml before changing.
CHOST="x86_64-pc-linux-gnu"
# These are the USE flags that were used in addition to what is provided by the
# profile used for building.
USE="bindist mmx sse sse2"
PORTDIR="/usr/portage"
DISTDIR="${PORTDIR}/distfiles"
PKGDIR="${PORTDIR}/packages"'''

                makeconf.write(lines)
            mkdir("-p", "etc/portage/metadata")
            with open("etc/portage/metadata/layout.conf", 'w') as layoutconf:
                lines = '''masters = gentoo'''
                layoutconf.write(lines)
            cp("/etc/resolv.conf", "etc/resolv.conf")


class Eix(GentooGroup):
    """
    Represents the package eix from the portage tree.

    Building this class will create bare gentoo and compile eix.
    """

    class Factory:
        """
        The factory class for the package eix.
        """

        def create(self, exp):
            """
            Creates an instance of the Eix class.

            Return:
                Eix object
            """
            return Eix(exp, "eix")

    ProjectFactory.addFactory("Eix", Factory())

    def build(self):
        from pprof.utils.run import run, uchroot
        with local.cwd(self.builddir):
            with local.env(CC="/usr/bin/gcc", CXX="/usr/bin/g++", USE="tinfo"):
                run(uchroot()["/usr/bin/emerge", "ncurses"])
            run(uchroot()["/usr/bin/emerge", "eix"])

    def run_tests(self, experiment):
        pass
