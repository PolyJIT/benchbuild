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
import os

from benchbuild.utils.cmd import cp  # pylint: disable=E0401
from benchbuild.utils.compiler import wrap_cc_in_uchroot, wrap_cxx_in_uchroot
from benchbuild import project
from benchbuild.utils.path import mkfile_uchroot, mkdir_uchroot
from benchbuild.utils.path import list_to_path
from benchbuild.utils.run import uchroot_env, uchroot_mounts
from benchbuild.settings import CFG
from benchbuild.utils import container
from benchbuild.utils.container import Gentoo


class GentooGroup(project.Project):
    """Gentoo ProjectGroup is the base class for every portage build."""

    GROUP = 'gentoo'
    CONTAINER = Gentoo()
    SRC_FILE = None

    def __init__(self, exp):
        super(GentooGroup, self).__init__(exp, "gentoo")

    def build(self):
        pass

    def download(self):
        if not CFG["unionfs"]["enable"].value():
            container.unpack_container(
                project.Project.CONTAINER, self.builddir)

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
PYTHON_TARGETS="python2_7 python3_5"
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
        p_paths, p_libs = uchroot_env(CFG["container"]["prefixes"].value())

        with open(path, 'w') as bashrc:
            lines = '''
export PATH="{0}:${{PATH}}"
export LD_LIBRARY_PATH="{1}:${{LD_LIBRARY_PATH}}"
'''.format(list_to_path(paths + p_paths),
           list_to_path(libs + p_libs))

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

        if os.path.exists(str(config_file)):
            paths, libs = \
                    uchroot_env(
                        uchroot_mounts(
                            "mnt",
                            CFG["container"]["mounts"].value()))
            UCHROOT_CFG = CFG
            UCHROOT_CFG["plugins"]["projects"] = []
            UCHROOT_CFG["env"]["compiler_path"] = paths
            UCHROOT_CFG["env"]["compiler_ld_library_path"] = libs

            UCHROOT_CFG["env"]["binary_path"] = paths
            UCHROOT_CFG["env"]["binary_ld_library_path"] = libs

            UCHROOT_CFG["env"]["lookup_path"] = paths
            UCHROOT_CFG["env"]["lookup_ld_library_path"] = libs

            mkfile_uchroot("/.benchbuild.yml")
            UCHROOT_CFG.store(".benchbuild.yml")

        wrap_cc_in_uchroot(self.cflags, self.ldflags, self.compiler_extension)
        wrap_cxx_in_uchroot(self.cflags, self.ldflags, self.compiler_extension)
