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
import logging

from plumbum import ProcessExecutionError, local

from benchbuild import project
from benchbuild.settings import CFG
from benchbuild.utils import container
from benchbuild.utils.cmd import cp
from benchbuild.utils.compiler import wrap_cc_in_uchroot, wrap_cxx_in_uchroot
from benchbuild.utils.container import Gentoo
from benchbuild.utils.path import list_to_path, mkdir_uchroot, mkfile_uchroot
from benchbuild.utils.run import uretry, uchroot, uchroot_env, uchroot_mounts

LOG = logging.getLogger(__name__)


def write_makeconfig(path):
    """
    Write a valid gentoo make.conf file to :path:.

    Args:
        path - The output path of the make.conf
    """

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
        http_proxy = CFG["gentoo"]["http_proxy"].value()
        if http_proxy is not None:
            http_s = "http_proxy={0}".format(str(http_proxy))
            https_s = "https_proxy={0}".format(str(http_proxy))
            makeconf.write(http_s + "\n")
            makeconf.write(https_s + "\n")

        ftp_proxy = CFG["gentoo"]["ftp_proxy"].value()
        if ftp_proxy is not None:
            fp_s = "ftp_proxy={0}".format(str(ftp_proxy))
            makeconf.write(fp_s + "\n")

        rsync_proxy = CFG["gentoo"]["rsync_proxy"].value()
        if rsync_proxy is not None:
            rp_s = "RSYNC_PROXY={0}".format(str(rsync_proxy))
            makeconf.write(rp_s + "\n")


def write_bashrc(path):
    """
    Write a valid gentoo bashrc file to :path:.

    Args:
        path - The output path of the make.conf
    """

    mkfile_uchroot("/etc/portage/bashrc")
    paths, libs = uchroot_env(
        uchroot_mounts("mnt", CFG["container"]["mounts"].value()))
    p_paths, p_libs = uchroot_env(CFG["container"]["prefixes"].value())

    with open(path, 'w') as bashrc:
        lines = '''
export PATH="{0}:${{PATH}}"
export LD_LIBRARY_PATH="{1}:${{LD_LIBRARY_PATH}}"
'''.format(list_to_path(paths + p_paths), list_to_path(libs + p_libs))

        bashrc.write(lines)


def write_layout(path):
    """
    Write a valid gentoo layout file to :path:.

    Args:
        path - The output path of the layout.conf
    """

    mkdir_uchroot("/etc/portage/metadata")
    mkfile_uchroot("/etc/portage/metadata/layout.conf")
    with open(path, 'w') as layoutconf:
        lines = '''masters = gentoo'''
        layoutconf.write(lines)


def write_wgetrc(path):
    """
    Write a valid gentoo wgetrc file to :path:.

    Args:
        path - The output path of the wgetrc
    """
    mkfile_uchroot("/etc/wgetrc")

    with open(path, 'w') as wgetrc:
        http_proxy = CFG["gentoo"]["http_proxy"].value()
        ftp_proxy = CFG["gentoo"]["ftp_proxy"].value()
        if http_proxy is not None:
            http_s = "http_proxy = {0}".format(str(http_proxy))
            https_s = "https_proxy = {0}".format(str(http_proxy))
            wgetrc.write("use_proxy = on\n")
            wgetrc.write(http_s + "\n")
            wgetrc.write(https_s + "\n")

        if ftp_proxy is not None:
            fp_s = "ftp_proxy={0}".format(str(ftp_proxy))
            wgetrc.write(fp_s + "\n")


class GentooGroup(project.Project):
    """Gentoo ProjectGroup is the base class for every portage build."""

    GROUP = 'gentoo'
    CONTAINER = Gentoo()
    SRC_FILE = None

    def build(self):
        pass

    def __setup_benchbuild(self):
        benchbuild = uchroot()["/usr/bin/benchbuild"]

        def requires_update():
            try:
                bb_version = benchbuild("--version")
                LOG.debug("bb version: %s", bb_version)
            except ProcessExecutionError as err:
                LOG.error("Querying Benchbuild inside container failed")
                LOG.debug("Reason: %s", str(err))
            return True

        if not requires_update():
            return

        LOG.debug("Upgrading BenchBuild.")
        src_dir = CFG["source_dir"].value()
        have_src = src_dir is not None
        if have_src:
            src_dir = local.path(str(src_dir))
            mount = {"src": src_dir, "tgt": "benchbuild"}
            mounts = CFG["container"]["mounts"].value()
            CFG["container"]["mounts"] = [mount]
            uretry(uchroot()["/usr/bin/pip", "install", "/mnt/benchbuild"])
            CFG["container"]["mounts"] = mounts
        else:
            uretry(uchroot()["/usr/bin/pip", "install", "--upgrade",
                             "benchbuild"])

    def compile(self):
        if not CFG["unionfs"]["enable"].value():
            container.unpack_container(self.container, self.builddir)

        write_bashrc("etc/portage/bashrc")
        write_makeconfig("etc/portage/make.conf")
        write_wgetrc("etc/wgetrc")
        write_layout("etc/portage/metadata/layout.conf")

        mkfile_uchroot("/etc/resolv.conf")
        cp("/etc/resolv.conf", "etc/resolv.conf")

        config_file = local.path(str(CFG["config_file"]))

        if config_file.exists():
            paths, libs = \
                    uchroot_env(
                        uchroot_mounts(
                            "mnt",
                            CFG["container"]["mounts"].value()))
            uchroot_cfg = CFG
            uchroot_cfg["plugins"]["projects"] = []

            uchroot_cfg["env"]["path"] = paths
            uchroot_cfg["env"]["ld_library_path"] = libs

            mkfile_uchroot("/.benchbuild.yml")
            uchroot_cfg.store(".benchbuild.yml")

        wrap_cc_in_uchroot(self)
        wrap_cxx_in_uchroot(self)

        self.__setup_benchbuild()
