"""
The Gentoo module for running tests on builds from the portage tree.

This will install a stage3 image of gentoo together with a recent snapshot
of the portage tree. For building / executing arbitrary projects successfully
it is necessary to keep the installed image as close to the host system as
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
from pprof.utils.compiler import wrap_cc_in_uchroot, wrap_cxx_in_uchroot
from pprof import project
from pprof.utils.run import run, uchroot
from pprof.utils.downloader import Wget
from pprof.settings import CFG
from lazy import lazy

def cached(func):
    ret = None
    def call_or_cache(*args, **kwargs):
        nonlocal ret
        if ret is None:
            ret = func(*args, **kwargs)
        return ret
    return call_or_cache

@cached
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


class GentooGroup(project.Project):
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
        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)

            cp(CFG["src_dir"].value() + "/bin/uchroot", "uchroot")
            run(fakeroot["tar", "xfj", self.src_file])
            rm(self.src_file)
            with local.cwd(self.builddir + "/usr"):
                Wget(self.src_uri_portage, self.src_file_portage)
                run(tar["xfj", self.src_file_portage])
                rm(self.src_file_portage)

    def write_wgetrc(self, path):
        with open(path, 'w') as wgetrc:
            hp = CFG["gentoo"]["http_proxy"].value()
            fp = CFG["gentoo"]["ftp_proxy"].value()
            if hp is not None:
                http_s = "http_proxy = {}".format(str(hp))
                https_s = "https_proxy = {}".format(str(hp))
                wgetrc.write("use_proxy = on\n")
                wgetrc.write(http_s + "\n")
                wgetrc.write(https_s + "\n")

            if fp is not None:
                fp_s = "ftp_proxy={}".format(str(fp))
                wgetrc.write(fp_s + "\n")

    def write_makeconfig(self, path):
        with open(path, 'w') as makeconf:
            lines = '''
CFLAGS="-O2 -pipe"
CXXFLAGS="${CFLAGS}"
FEATURES="-sandbox -usersandbox -usersync -xattr"
CC="/clang"
CXX="/clang++"

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
            hp = CFG["gentoo"]["http_proxy"].value()
            if hp is not None:
                http_s = "http_proxy={}".format(str(hp))
                https_s = "https_proxy={}".format(str(hp))
                makeconf.write(http_s + "\n")
                makeconf.write(https_s + "\n")

            fp = CFG["gentoo"]["ftp_proxy"].value()
            if fp is not None:
                fp_s = "ftp_proxy={}".format(str(fp))
                makeconf.write(fp_s + "\n")

            rp = CFG["gentoo"]["rsync_proxy"].value()
            if rp is not None:
                rp_s = "RSYNC_PROXY={}".format(str(rp))
                makeconf.write(rp_s + "\n")


    def write_bashrc(self, path):
        with open(path, 'w') as bashrc:
            lines = '''
export PATH="/llvm/bin:/pprof/bin:${PATH}"
export LD_LIBRARY_PAT=H"/llvm/lib:/pprof/lib:${LD_LIBRARY_PATH}"
'''
            bashrc.write(lines)

    def write_layout(self, path):
        with open(path, 'w') as layoutconf:
            lines = '''masters = gentoo'''
            layoutconf.write(lines)

    def configure(self):
        with local.cwd(self.builddir):
            self.write_bashrc("etc/portage/bashrc")
            self.write_makeconfig("etc/portage/make.conf")
            self.write_wgetrc("etc/wgetrc")

            mkdir("-p", "etc/portage/metadata")
            self.write_layout("etc/portage/metadata/layout.conf")
            cp("/etc/resolv.conf", "etc/resolv.conf")

            config_file = CFG["config_file"].value()
            if path.exists(str(config_file)):
                cp(config_file, path.basename(config_file))

            wrap_cc_in_uchroot(self.cflags, self.ldflags,
                               self.compiler_extension, "/llvm/bin")
            wrap_cxx_in_uchroot(self.cflags, self.ldflags,
                                self.compiler_extension, "/llvm/bin")


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

        root = CFG["tmp_dir"].value()
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


class AutoPolyJITDepsStage3(GentooGroup):
    """
    A project that installs all dependencies for PolyJIT in the stage3 image.
    """
    NAME = "polyjit-deps"
    DOMAIN = "debug"

    def build(self):
        import sys
        # Don't do something when running non-interactive.
        if not sys.stdout.isatty():
            return

        from plumbum import FG
        from pprof.utils.downloader import update_hash
        from logging import info

        root = CFG["tmp_dir"].value()
        src_file = self.src_file + ".new"
        with local.cwd(self.builddir):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            with local.env(CC="gcc", CXX="g++", ACCEPT_KEYWORDS="~amd64"):
                with local.env(USE="-filecaps"):
                    run(emerge_in_chroot["likwid"])
                with local.env(USE="static-libs"):
                    run(emerge_in_chroot["dev-libs/libpfm"])
                run(emerge_in_chroot["dev-libs/papi"])
                run(emerge_in_chroot["time"])
                run(emerge_in_chroot["fakeroot"])

            tgt_path = path.join(root, self.src_file)
            tgt_path_new = path.join(root, src_file)
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

        root = CFG["tmp_dir"].value()
        src_file = self.src_file + ".new"
        with local.cwd(self.builddir):
            mkdir("-p", "pprof-src")
            w_pprof_src = uchroot("-m",
                                  "{}:pprof-src".format(str(CFG["src_dir"])))
            pip_in_uchroot = w_pprof_src["/usr/bin/pip3"]
            pip_in_uchroot("install", "--upgrade", "/pprof-src/")

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
