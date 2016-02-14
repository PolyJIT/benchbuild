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
from os import path
from plumbum.cmd import cp, tar, mv, fakeroot, rm  # pylint: disable=E0401
from plumbum.cmd import mkdir, curl, cut, tail  # pylint: disable=E0401
from plumbum import local
from pprof.project import Project
from pprof.utils.run import run, uchroot
from pprof.utils.downloader import Wget
from lazy import lazy


def latest_src_uri():
    """
    Get the latest src_uri for a stage 3 tarball.

    Returns (str):
        Latest src_uri from gentoo's distfiles mirror.
    """
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
    GROUP = 'gentoo'

    def __init__(self, exp):
        super(GentooGroup, self).__init__(exp, "gentoo")

    src_dir = "gentoo"
    src_file = src_dir + ".tar.bz2"

    @lazy
    def src_uri(self):  # pylint: disable=R0201
        """Fetches the lates src_uri from the gentoo mirrors."""
        return "http://distfiles.gentoo.org/releases/amd64/autobuilds/{0}" \
                .format(latest_src_uri())

    # download location for portage files
    src_uri_portage = "ftp://sunsite.informatik.rwth-aachen.de/pub/Linux/"\
                    "gentoo/snapshots/portage-latest.tar.bz2"
    src_file_portage = "portage_snap.tar.bz2"

    def build(self):
        pass

    def download(self):
        from pprof.settings import config
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
        with local.cwd(self.builddir):
            with open("etc/portage/make.conf", 'w') as makeconf:
                lines = '''
PATH="/llvm/bin:/pprof/bin:${PATH}"
LD_LIBRARY_PATH="/llvm/lib:/pprof/lib:${LD_LIBRARY_PATH}"
CFLAGS="-O2 -pipe"
CXXFLAGS="${CFLAGS}"
FEATURES="-sandbox -usersandbox -usersync -xattr"
CC="/llvm/bin/clang"
CXX="/llvm/bin/clang++"

PORTAGE_USERNAME = "root"
PORTAGE_GRPNAME = "root"
PORTAGE_INST_GID = 0
PORTAGE_INST_UID = 0

CHOST="x86_64-pc-linux-gnu"
USE="bindist mmx sse sse2"
PORTDIR="/usr/portage"
DISTDIR="${PORTDIR}/distfiles"
PKGDIR="${PORTDIR}/packages"
'''

                makeconf.write(lines)

            mkdir("-p", "etc/portage/metadata")
            with open("etc/portage/metadata/layout.conf", 'w') as layoutconf:
                lines = '''masters = gentoo'''
                layoutconf.write(lines)
            cp("/etc/resolv.conf", "etc/resolv.conf")


class PrepareStage3(GentooGroup):
    """
    A project that can be used for interactive stage3 generation.
    """
    NAME = "stage3"
    DOMAIN = "debug"

    def build(self):
        import sys
        # Don't do something when running non-interactive.
        if not sys.stdout.isatty():
            return

        from plumbum import FG
        from pprof.utils.downloader import update_hash
        from logging import info
        from pprof.settings import config

        root = config["tmpdir"]
        src_file = self.src_file + ".new"
        with local.cwd(self.builddir):
            bash_in_uchroot = uchroot()["/bin/bash"]
            print("Entering User-Chroot. Prepare your image and "
                  "type 'exit' when you are done.")
            bash_in_uchroot & FG  # pylint: disable=W0104
            tgt_path = path.join(root, self.src_file)
            tgt_path_new = path.join(root, src_file)
            print("Packing new stage3 image. "
                  "This will replace the original one at: ", tgt_path)
            tar("cjf", tgt_path_new, ".")
            update_hash(src_file, root)
            mv(path.join(root, src_file), tgt_path)

    def run_tests(self, experiment):
        pass


class AutoPrepareStage3(GentooGroup):
    """
    A project that can be used to install pprof in the stage3 archive.
    """
    NAME = "auto-stage3"
    DOMAIN = "debug"

    def build(self):
        import sys
        # Don't do something when running non-interactive.
        if not sys.stdout.isatty():
            return

        from plumbum import FG
        from pprof.utils.downloader import update_hash
        from logging import info
        from pprof.settings import config

        root = config["tmpdir"]
        src_file = self.src_file + ".new"
        with local.cwd(self.builddir):
            mkdir("-p", "pprof-src")
            w_pprof_src = uchroot("-m", "{}:pprof-src".format(config[
                "sourcedir"]))
            pip_in_uchroot = w_pprof_src["/usr/bin/pip3"]
            pip_in_uchroot["install", "--upgrade", "/pprof-src/"] & FG

            tgt_path = path.join(root, self.src_file)
            tgt_path_new = path.join(root, src_file)
            tar("cjf", tgt_path_new, ".")
            update_hash(src_file, root)
            mv(path.join(root, src_file), tgt_path)

    def run_tests(self, experiment):
        pass


class Eix(GentooGroup):
    """
    Represents the package eix from the portage tree.

    Building this class will create bare gentoo and compile eix.
    """
    NAME = 'eix'
    DOMAIN = 'debug'

    def build(self):
        with local.cwd(self.builddir):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            run(emerge_in_chroot["eix"])

    def run_tests(self, experiment):
        pass


class BZip2(GentooGroup):
    """
        app-arch/bzip2
    """
    NAME = "gentoo-bzip2"
    DOMAIN = "app-arch"

    test_url = "http://lairosiel.de/dist/"
    test_archive = "compression.tar.gz"
    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    def prepare(self):
        super(BZip2, self).prepare()

        test_archive = self.test_archive
        test_url = self.test_url + test_archive
        with local.cwd(self.builddir):
            Wget(test_url, test_archive)
            tar("fxz", test_archive)

    def build(self):
        with local.cwd(self.builddir):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            run(emerge_in_chroot["app-arch/bzip2"])

    def run_tests(self, experiment):
        from pprof.project import wrap

        wrap(path.join(self.builddir, "bin", "bzip2"), experiment)
        bzip2 = uchroot()["/bin/bzip2"]

        # Compress
        run(bzip2["-f", "-z", "-k", "--best", "compression/text.html"])
        run(bzip2["-f", "-z", "-k", "--best", "compression/chicken.jpg"])
        run(bzip2["-f", "-z", "-k", "--best", "compression/control"])
        run(bzip2["-f", "-z", "-k", "--best", "compression/input.source"])
        run(bzip2["-f", "-z", "-k", "--best", "compression/liberty.jpg"])

        # Decompress
        run(bzip2["-f", "-k", "--decompress", "compression/text.html.bz2"])
        run(bzip2["-f", "-k", "--decompress", "compression/chicken.jpg.bz2"])
        run(bzip2["-f", "-k", "--decompress", "compression/control.bz2"])
        run(bzip2["-f", "-k", "--decompress", "compression/input.source.bz2"])
        run(bzip2["-f", "-k", "--decompress", "compression/liberty.jpg.bz2"])
