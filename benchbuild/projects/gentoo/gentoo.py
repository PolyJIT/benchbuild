"""
The Gentoo module for running tests on builds from the portage tree.

This will install a stage3 image of gentoo together with a recent snapshot
of the portage tree. For building / executing arbitrary projects successfully
it is necessary to keep the installed image as close to the host system as
possible.
In order to speed up your experience, you can replace the stage3 image that we
pull from the distfiles mirror with a new image that contains all necessary
dependencies for your experiments. Make sure you update the hash alongside
the gentoo image in benchbuild's source directory.

"""
from os import path
from benchbuild.utils.cmd import cp, tar, mv, rm  # pylint: disable=E0401
from plumbum import local
from benchbuild.utils.compiler import wrap_cc_in_uchroot, wrap_cxx_in_uchroot
from benchbuild import project
from benchbuild.utils.run import run, uchroot, uchroot_no_llvm
from benchbuild.utils.path import mkfile_uchroot, mkdir_uchroot
from benchbuild.utils.path import list_to_path
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import uchroot_env, uchroot_mounts
from benchbuild.settings import CFG
from benchbuild.utils import container
from benchbuild.utils.container import Gentoo


class GentooGroup(project.Project):
    """
    Gentoo ProjectGroup is the base class for every portage build.
    """
    GROUP = 'gentoo'
    CONTAINER = Gentoo()

    def __init__(self, exp):
        super(GentooGroup, self).__init__(exp, "gentoo")

    src_dir = "gentoo"
    src_file = src_dir + ".tar.bz2"

    def build(self):
        pass

    def download(self):
        if not project.CFG["unionfs"]["enable"].value() == True:
            container.unpack_container(self.builddir)

    def write_wgetrc(self, path):
        mkfile_uchroot("/etc/wgetrc")

        with open(path, 'w') as wgetrc:
            hp = CFG["gentoo"]["http_proxy"].value()
            fp = CFG["gentoo"]["ftp_proxy"].value()
            if hp is not None:
                http_s = "http_proxy = {0}".format(str(hp))
                https_s = "https_proxy = {0}".format(str(hp))
                wgetrc.write("use_proxy = on\n")
                wgetrc.write(http_s + "\n")
                wgetrc.write(https_s + "\n")

            if fp is not None:
                fp_s = "ftp_proxy={0}".format(str(fp))
                wgetrc.write(fp_s + "\n")

    def write_makeconfig(self, path):
        mkfile_uchroot("/etc/portage/make.conf")
        with open(path, 'w') as makeconf:
            lines = '''
PORTAGE_USERNAME=root
PORTAGE_GROUPNAME=root
CFLAGS="-O2 -pipe"
CXXFLAGS="${CFLAGS}"
FEATURES="-xattr"
CC="/clang"
CXX="/clang++"

CHOST="x86_64-pc-linux-gnu"
USE="bindist mmx sse sse2"
PORTDIR="/usr/portage"
DISTDIR="${PORTDIR}/distfiles"
PKGDIR="${PORTDIR}/packages"
'''

            makeconf.write(lines)
            hp = CFG["gentoo"]["http_proxy"].value()
            if hp is not None:
                http_s = "http_proxy={0}".format(str(hp))
                https_s = "https_proxy={0}".format(str(hp))
                makeconf.write(http_s + "\n")
                makeconf.write(https_s + "\n")

            fp = CFG["gentoo"]["ftp_proxy"].value()
            if fp is not None:
                fp_s = "ftp_proxy={0}".format(str(fp))
                makeconf.write(fp_s + "\n")

            rp = CFG["gentoo"]["rsync_proxy"].value()
            if rp is not None:
                rp_s = "RSYNC_PROXY={0}".format(str(rp))
                makeconf.write(rp_s + "\n")

    def write_bashrc(self, path):
        mkfile_uchroot("/etc/portage/bashrc")
        paths, libs = uchroot_env(
                uchroot_mounts("mnt",
                    CFG["container"]["mounts"].value()))

        with open(path, 'w') as bashrc:
            lines = '''
export PATH="{0}:${{PATH}}"
export LD_LIBRARY_PATH="{1}:${{LD_LIBRARY_PATH}}"
'''.format(list_to_path(paths),
           list_to_path(libs))

            bashrc.write(lines)

    def write_layout(self, path):
        mkdir_uchroot("/etc/portage/metadata")
        mkfile_uchroot("/etc/portage/metadata/layout.conf")
        with open(path, 'w') as layoutconf:
            lines = '''masters = gentoo'''
            layoutconf.write(lines)

    def configure(self):
        self.write_bashrc("etc/portage/bashrc")
        self.write_makeconfig("etc/portage/make.conf")
        self.write_wgetrc("etc/wgetrc")
        self.write_layout("etc/portage/metadata/layout.conf")

        mkfile_uchroot("/etc/resolv.conf")
        cp("/etc/resolv.conf", "etc/resolv.conf")

        config_file = CFG["config_file"].value()

        if path.exists(str(config_file)):
            with open("log.file", 'w') as outf:
                paths, libs = \
                        uchroot_env(
                            uchroot_mounts("mnt",
                                CFG["container"]["mounts"].value()))
                UCHROOT_CFG = CFG
                UCHROOT_CFG["env"]["compiler_path"] = paths
                UCHROOT_CFG["env"]["compiler_ld_library_path"] = libs

                UCHROOT_CFG["env"]["binary_path"] = paths
                UCHROOT_CFG["env"]["binary_ld_library_path"] = libs

                UCHROOT_CFG["env"]["lookup_path"] = paths
                UCHROOT_CFG["env"]["lookup_ld_library_path"] = libs

                mkfile_uchroot("/.benchbuild.json")
                UCHROOT_CFG.store(".benchbuild.json")

        wrap_cc_in_uchroot(self.cflags, self.ldflags, self.compiler_extension)
        wrap_cxx_in_uchroot(self.cflags, self.ldflags, self.compiler_extension)


class PrepareStage3(GentooGroup):
    """
    A project that can be used for interactive stage3 generation.
    """
    NAME = "stage3"
    DOMAIN = "debug"

    # download location for portage files
    src_uri_portage = "ftp://sunsite.informatik.rwth-aachen.de/pub/Linux/"\
                      "gentoo/snapshots/portage-latest.tar.bz2"
    src_file_portage = "portage_snap.tar.bz2"

    def download(self):
        super(PrepareStage3, self).download()

        with local.cwd(self.builddir + "/usr"):
            Wget(self.src_uri_portage, self.src_file_portage)
            run(tar["xfj", self.src_file_portage])
            rm(self.src_file_portage)

    def build(self):
        import sys
        # Don't do something when running non-interactive.
        if not sys.stdout.isatty():
            return

        from plumbum import FG
        from benchbuild.utils.downloader import update_hash

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


class AutoPolyJITDepsStage3(PrepareStage3):
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

        from benchbuild.utils.downloader import update_hash

        root = CFG["tmp_dir"].value()
        src_file = self.src_file + ".new"
        with local.cwd(self.builddir):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            emerge_boost = uchroot(uid=501, gid=10)["/usr/bin/emerge"]
            with local.env(CC="gcc", CXX="g++", ACCEPT_KEYWORDS="~amd64"):
                run(emerge_in_chroot["--sync"])
                with local.env(USE="-filecaps"):
                    run(emerge_in_chroot["likwid"])
                with local.env(USE="static-libs"):
                    run(emerge_in_chroot["dev-libs/libpfm"])
                run(emerge_in_chroot["dev-libs/papi"])
                run(emerge_in_chroot["sys-process/time"])
                run(emerge_boost["dev-utils/boost-build"])
                run(emerge_boost["dev-libs/boost"])

            tgt_path = path.join(root, self.src_file)
            tgt_path_new = path.join(root, src_file)
            tar("cjf", tgt_path_new, ".")
            update_hash(src_file, root)
            mv(path.join(root, src_file), tgt_path)

    def run_tests(self, experiment):
        pass


class AutoPrepareStage3(GentooGroup):
    """
    A project that can be used to install benchbuild in the stage3 archive.
    """
    NAME = "auto-stage3"
    DOMAIN = "debug"

    def build(self):
        from benchbuild.utils.downloader import update_hash

        uchroot = uchroot_no_llvm

        root = CFG["tmp_dir"].value()
        src_file = self.src_file + ".new"
        with local.cwd(self.builddir):
            sed_in_chroot = uchroot()["/bin/sed"]
            run(sed_in_chroot["-i", '/CC=/d', "/etc/portage/make.conf"])
            run(sed_in_chroot["-i", '/CXX=/d', "/etc/portage/make.conf"])
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            #run(emerge_in_chroot["dev-python/pip"])

            with local.env(CC="gcc", CXX="g++"):
                #    run(emerge_in_chroot["dev-db/postgresql"])
                #    run(emerge_in_chroot["net-misc/curl"])

                # We need the unstable portage version
                with local.env(ACCEPT_KEYWORDS="~*", LD_LIBRARY_PATH=""):
                    run(emerge_in_chroot["--autounmask-only=y", "-uUDN",
                                         "--with-bdeps=y", "@world"])
                    run(emerge_in_chroot["-uUDN", "--with-bdeps=y", "@world"])
                    run(emerge_in_chroot["--autounmask-only=y",
                                         "=sys-libs/ncurses-6.0-r1:0/6"])
                    run(emerge_in_chroot["=sys-libs/ncurses-6.0-r1:0/6"])
            #        run(emerge_in_chroot["sys-apps/portage"])

            tgt_path = path.join(root, self.src_file)
            tgt_path_new = path.join(root, src_file)
            tar("cjf", tgt_path_new, ".")
            update_hash(src_file, root)
            mv(path.join(root, src_file), tgt_path)

    def run_tests(self, experiment):
        pass
