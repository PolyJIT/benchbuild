#!/usr/bin/env python
# encoding: utf-8

from pprof.project import Project, ProjectFactory
from plumbum import local

class GentooGroup(Project):

    """
    Gentoo ProjectGroup for running the gentoo test suite.

    The following packages are required to run GentooGroup
    * fakeroot

    """

    def __init__(self, exp, name):
        super(GentooGroup, self).__init__(exp, name, "gentoo", "gentoo")

    src_dir = "gentoo"
    src_file = src_dir + ".tar.bz2"

    # download location for gentoo stage3 tarball
    day = "20151119"
    src_uri = "http://distfiles.gentoo.org/releases/amd64/current-stage3-"\
            "amd64/" + "stage3-amd64-" + day + ".tar.bz2"

    # download location for portage files
    src_uri_portage = "ftp://sunsite.informatik.rwth-aachen.de/pub/Linux/"\
                    "gentoo/snapshots/portage-latest.tar.bz2"
    src_file_portage = "portage_snap.tar.bz2"

    # test dirs
    test_suite_dir = "TODO"
    test_suite_uri = "TODO"

    def download(self):
        from pprof.utils.downloader import Wget
        from pprof.utils.run import run
        from plumbum import FG
        from plumbum.cmd import virtualenv, cp, tar, fakeroot, rm
        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)

            # TODO replace with standart path
            cp("/home/sattlerf/gentoo/uchroot_2","uchroot")
            run(fakeroot["tar", "xfj", self.src_file])
            rm(self.src_file)
            with local.cwd(self.builddir + "/usr"):
                Wget(self.src_uri_portage, self.src_file_portage)
                run(tar["xfj", self.src_file_portage])
                rm(self.src_file_portage)

    def configure(self):
        from plumbum.cmd import mkdir, rm, cp
        with local.cwd(self.builddir):
            with open("etc/portage/make.conf", 'w') as makeconf:
                lines = '''# These settings were set by the catalyst build '''\
                        '''script that automatically
# built this stage.
# Please consult /usr/share/portage/config/make.conf.example for a more
# detailed example.
CFLAGS="-O2 -pipe"
CXXFLAGS="${CFLAGS}"

FEATURES="-sandbox -usersandbox fakeroot -usersync -xattr"

# set compiler
#CC="/usr/bin/gcc"
#CXX="/usr/bin/g++"
CC="/llvm/bin/clang"
CXX="/llvm/bin/clang++"
#CC="/usr/bin/clang"
#CXX="/usr/bin/clang++"

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
            with open("etc/resolv.conf", 'w') as resolfconf:
                cp("/etc/resolv.conf","etc/resolv.conf")
            # cp jit into gentoo

    @property
    def execWithChroot(self):
        """
        Returns a plumbum cmd object that allows the user to call a cmd in
        the uchroot.

        Return:
            chroot cmd object
        """

        from plumbum.cmd import binddev
        uchroot = local["./uchroot"]
        return uchroot["-C", "-w", "/", "-r", ".", "-u", "0", "-g", "0", "--"]

    @property
    def execWithChrootJIT(self):
        from pprof.settings import config
        from plumbum.cmd import mkdir

        mkdir("-p", "llvm")
        uchroot = local["./uchroot"]
        return uchroot["-C", "-w", "/", "-r", ".", "-m", config["llvmdir"] + ":llvm","-u", "0", "-g", "0", "--"]

class Eix(GentooGroup):

    class Factory:

        def create(self, exp):
            return Eix(exp, "eix")
    ProjectFactory.addFactory("Eix", Factory())

    def build(self):
        from pprof.utils.run import run
        with local.cwd(self.builddir):
            with local.env(CC="/usr/bin/gcc", CXX="/usr/bin/g++", USE="tinfo"):
                run(self.execWithChrootJIT["/usr/bin/emerge", "ncurses"])
            run(self.execWithChrootJIT["/usr/bin/emerge", "eix"])

    def run_tests(self, experiment):
        pass


