from abc import abstractmethod
import logging
import os
import sys

from benchbuild.utils.cmd import tar, mkdir, mv, rm, bash, cp
from benchbuild.settings import CFG, update_env
from benchbuild.utils import log
from benchbuild.utils.bootstrap import find_package, install_uchroot
from benchbuild.utils.path import mkfile_uchroot, mkdir_uchroot
from benchbuild.utils.path import list_to_path
from benchbuild.utils.container import Gentoo
from benchbuild.utils.run import (run, uchroot, uchroot_with_mounts,
                                  uchroot_no_args, uchroot_env,
                                  uchroot_mounts)
from benchbuild.utils.downloader import Copy, update_hash
from benchbuild.utils.user_interface import ask
from plumbum import cli, local, TF, FG, ProcessExecutionError

LOG = logging.getLogger(__name__)


def clean_directories(builddir, in_dir=True, out_dir=True):
    """Remove the in and out of the container if confirmed by the user."""
    with local.cwd(builddir):
        if in_dir and os.path.exists("container-in") and ask(
                "Should I delete '{0}'?".format(os.path.abspath(
                    "container-in"))):
            rm("-rf", "container-in")
        if out_dir and os.path.exists("container-out") and ask(
                "Should I delete '{0}'?".format(os.path.abspath(
                    "container-out"))):
            rm("-rf", "container-out")


def setup_directories(builddir):
    """Create the in and out directories of the container."""
    with local.cwd(builddir):
        if not os.path.exists("container-in"):
            mkdir("-p", "container-in")
        if not os.path.exists("container-out"):
            mkdir("-p", "container-out")


def setup_container(builddir, container):
    """Prepare the container and returns the path where it can be found."""
    with local.cwd(builddir):
        container_filename = str(container).split(os.path.sep)[-1]
        container_in = os.path.join("container-in", container_filename)
        Copy(container, container_in)
        uchroot = uchroot_no_args()

        with local.cwd("container-in"):
            uchroot = uchroot["-E", "-A", "-u", "0", "-g", "0", "-C", "-r",
                              "/", "-w", os.path.abspath("."), "--"]

        # Check, if we need erlent support for this archive.
        has_erlent = bash[
            "-c", "tar --list -f './{0}' | grep --silent '.erlent'".format(
                container_in)]
        has_erlent = (has_erlent & TF)

        # Unpack input container to: container-in
        if not has_erlent:
            cmd = local["/bin/tar"]["xf"]
            cmd = uchroot[cmd[container_filename]]
        else:
            cmd = tar["xf"]
            cmd = cmd[os.path.abspath(container_in)]

        with local.cwd("container-in"):
            cmd("--exclude=dev/*")
        rm(container_in)
    return os.path.join(builddir, "container-in")


def run_in_container(command, container_dir, mounts):
    """
    Run a given command inside a container.

    Mounts a directory as a container at the given mountpoint and tries to run
    the given command inside the new container.
    """
    with local.cwd(container_dir):
        uchroot = uchroot_with_mounts()
        uchroot = uchroot["-E", "-A", "-u", "0", "-g", "0", "-C", "-w",
                          "/", "-r", os.path.abspath(container_dir)]
        uchroot = uchroot["--"]

        cmd_path = os.path.join(container_dir, command[0].lstrip('/'))
        if not os.path.exists(cmd_path):
            LOG.error(
                "The command does not exist inside the container! %s",
                cmd_path)
            return

        cmd = uchroot[command]
        return cmd & FG


def pack_container(in_container, out_file):
    container_filename = os.path.split(out_file)[-1]
    out_container = os.path.join("container-out", container_filename)
    out_container = os.path.abspath(out_container)

    out_tmp_filename = os.path.basename(out_container)
    out_dir = os.path.dirname(out_container)

    # Pack the results to: container-out
    with local.cwd(in_container):
        tar("cjf", out_container, ".")
    c_hash = update_hash(out_tmp_filename, out_dir)
    if not os.path.exists(out_dir):
        mkdir("-p", out_dir)
    mv(out_container, out_file)
    mv(out_container + ".hash", out_file + ".hash")

    new_container = {"path": out_file, "hash": str(c_hash)}
    CFG["container"]["known"].value().append(new_container)


def setup_bash_in_container(builddir, container, outfile, mounts, shell):
    """
    Setup a bash environment inside a container.

    Creates a new chroot, which the user can use as a bash to run the wanted
    projects inside the mounted container, that also gets returned afterwards.
    """
    with local.cwd(builddir):
        # Switch to bash inside uchroot
        print("Entering bash inside User-Chroot. Prepare your image and "
              "type 'exit' when you are done. If bash exits with a non-zero"
              "exit code, no new container will be stored.")
        store_new_container = True
        try:
            run_in_container(shell, container, mounts)
        except ProcessExecutionError:
            store_new_container = False

        if store_new_container:  # pylint: disable=W0104
            print("Packing new container image.")
            pack_container(container, outfile)
            config_path = CFG["config_file"].value()
            CFG.store(config_path)
            print("Storing config in {0}".format(os.path.abspath(config_path)))


def find_hash(container_db, key):
    """Find the first container in the database with the given key."""
    for keyvalue in container_db:
        if keyvalue["hash"].startswith(key):
            return keyvalue["path"]
    return None


def set_input_container(container, cfg):
    """Save the input for the container in the configurations."""
    if not container:
        return False
    if os.path.exists(container):
        cfg["container"]["input"] = container
        return True
    return False


class MockObj(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ContainerStrategy(object):
    """Interfaces for the different containers chosen by the experiment."""

    @abstractmethod
    def run(self, context):
        pass


class BashStrategy(ContainerStrategy):
    """The user interface for setting up a bash inside the container."""

    def run(self, context):
        print("Entering a shell in the container.\nUse the exit "
              "command to leave the container.")
        setup_bash_in_container(context.builddir, context.in_container,
                                context.out_container, context.mounts,
                                context.shell)


class SetupPolyJITGentooStrategy(ContainerStrategy):
    """Interface of using gentoo as a container for an experiment."""

    def write_wgetrc(self, path):
        """Wget the project from a specified link."""
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
        """Create the stringed to be written in the settings."""
        mkfile_uchroot("/etc/portage/make.conf")
        with open(path, 'w') as makeconf:
            lines = '''
PORTAGE_USERNAME=root
PORTAGE_GROUPNAME=root
CFLAGS="-O2 -pipe"
CXXFLAGS="${CFLAGS}"
FEATURES="-xattr"

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
        """Write inside a bash and update the shell if necessary."""
        mkfile_uchroot("/etc/portage/bashrc")
        paths, libs = uchroot_env(
                uchroot_mounts("mnt", CFG["container"]["mounts"].value()))

        with open(path, 'w') as bashrc:
            lines = '''
export PATH="{0}:${{PATH}}"
export LD_LIBRARY_PATH="{1}:${{LD_LIBRARY_PATH}}"
'''.format(list_to_path(paths), list_to_path(libs))
            bashrc.write(lines)

    def write_layout(self, path):
        """Create a layout from the given path."""
        mkdir_uchroot("/etc/portage/metadata")
        mkfile_uchroot("/etc/portage/metadata/layout.conf")
        with open(path, 'w') as layoutconf:
            lines = '''masters = gentoo'''
            layoutconf.write(lines)

    def configure(self):
        """Configure the gentoo container for a PolyJIT experiment."""
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
                        uchroot_mounts("mnt",
                                       CFG["container"]["mounts"].value()))
            uchroot_cfg = CFG
            uchroot_cfg["env"]["path"] = paths
            uchroot_cfg["env"]["ld_library_path"] = libs

            uchroot_cfg["env"]["path"] = paths
            uchroot_cfg["env"]["ld_library_path"] = libs

            uchroot_cfg["env"]["path"] = paths
            uchroot_cfg["env"]["ld_library_path"] = libs

            mkfile_uchroot("/.benchbuild.json")
            uchroot_cfg.store(".benchbuild.json")

    def run(self, context):
        """Setup a gentoo container suitable for PolyJIT."""
        # Don't do something when running non-interactive.
        if not sys.stdout.isatty():
            return

        with local.cwd(context.in_container):
            self.configure()
            sed_in_chroot = uchroot()["/bin/sed"]
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            has_pkg = uchroot()["/usr/bin/qlist", "-I"]

            run(sed_in_chroot["-i", '/CC=/d', "/etc/portage/make.conf"])
            run(sed_in_chroot["-i", '/CXX=/d', "/etc/portage/make.conf"])

            packages = \
                CFG["container"]["strategy"]["polyjit"]["packages"].value()
            with local.env(CC="gcc", CXX="g++",
                           MAKEOPTS="-j{0}".format(CFG["jobs"].value())):
                if CFG["container"]["strategy"]["polyjit"]["sync"].value():
                    run(emerge_in_chroot["--sync"])
                if CFG["container"]["strategy"]["polyjit"]["upgrade"].value():
                    run(emerge_in_chroot["--autounmask-only=y", "-uUDN",
                                         "--with-bdeps=y", "@world"])
                run(emerge_in_chroot["-uUDN", "--with-bdeps=y", "@world"])
                for pkg in packages:
                    if (has_pkg[pkg["name"]] & TF):
                        continue
                    env = pkg["env"]
                    with local.env(**env):
                            run(emerge_in_chroot[pkg["name"]])

        print("Packing new container image.")
        with local.cwd(context.builddir):
            pack_container(context.in_container, context.out_container)


class Container(cli.Application):
    """Manage uchroot containers."""

    VERSION = CFG["version"].value()

    def __init__(self, exe):
        super(Container, self).__init__(exe)

    @cli.switch(["-i", "--input-file"], str, help="Input container path")
    def input_file(self, container):
        """Find the input path of a uchroot container."""
        p = os.path.abspath(container)
        if set_input_container(p, CFG):
            return

        p = find_hash(CFG["container"]["known"].value(), container)
        if set_input_container(p, CFG):
            return

        raise ValueError("The path '{0}' does not exist.".format(p))

    @cli.switch(["-o", "--output-file"], str, help="Output container path")
    def output_file(self, container):
        """Find and writes the output path of a chroot container."""
        p = os.path.abspath(container)
        if os.path.exists(p):
            if not ask("Path '{0}' already exists." " Overwrite?".format(p)):
                sys.exit(0)
        CFG["container"]["output"] = p

    @cli.switch(["-s", "--shell"],
                str,
                help="The shell command we invoke inside the container.")
    def shell(self, custom_shell):
        """The command to run inside the container."""
        CFG["container"]["shell"] = custom_shell

    @cli.switch(["-t", "-tmp-dir"],
                cli.ExistingDirectory,
                help="Temporary directory")
    def builddir(self, tmpdir):
        """Set the current builddir of the container."""
        CFG["build_dir"] = tmpdir

    @cli.switch(
        ["m", "--mount"],
        cli.ExistingDirectory,
        list=True,
        help="Mount the given directory under / inside the uchroot container")
    def mounts(self, user_mount):
        """Save the current mount of the container into the settings."""
        CFG["container"]["mounts"] = user_mount

    verbosity = cli.CountOf('-v', help="Enable verbose output")

    def main(self, *args):
        log.configure()
        _log = logging.getLogger()
        _log.setLevel({
            3: logging.DEBUG,
            2: logging.INFO,
            1: logging.WARNING,
            0: logging.ERROR
        }[self.verbosity])

        update_env()
        builddir = os.path.abspath(str(CFG["build_dir"].value()))
        if not os.path.exists(builddir):
            response = ask("The build directory {dirname} does not exist yet. "
                           "Should I create it?".format(dirname=builddir))

            if response:
                mkdir("-p", builddir)
                print("Created directory {0}.".format(builddir))

        setup_directories(builddir)


@Container.subcommand("run")
class ContainerRun(cli.Application):
    """Execute commannds inside a prebuilt container."""

    def main(self, *args):
        builddir = CFG["build_dir"].value()
        in_container = CFG["container"]["input"].value()
        mounts = CFG["container"]["mounts"].value()

        if (in_container is None) or not os.path.exists(in_container):
            in_is_file = False
            in_container = Gentoo().local
        else:
            in_is_file = os.path.isfile(in_container)
            if in_is_file:
                clean_directories(builddir)
                setup_directories(builddir)
                in_container = setup_container(builddir, in_container)

        run_in_container(args, in_container, mounts)
        clean_directories(builddir, in_is_file, False)


@Container.subcommand("create")
class ContainerCreate(cli.Application):
    """
    Create a new container with a predefined strategy.

    We offer a variety of creation policies for a new container. By default a
    basic 'spawn a bash' policy is used. This just leaves you inside a bash
    that is started in the extracted container. After customization you can
    exit the bash and pack up the result.
    """

    _strategy = BashStrategy()

    @cli.switch(["-S", "--strategy"],
                cli.Set("bash", "polyjit", case_sensitive=False),
                help="Defines the strategy used to create a new container.",
                mandatory=False)
    def strategy(self, strategy):
        self._strategy = {
            "bash": BashStrategy(),
            "polyjit": SetupPolyJITGentooStrategy()
        }[strategy]

    def main(self, *args):
        builddir = CFG["build_dir"].value()
        in_container = CFG["container"]["input"].value()
        out_container = CFG["container"]["output"].value()
        mounts = CFG["container"]["mounts"].value()
        shell = CFG["container"]["shell"].value()

        if (in_container is None) or not os.path.exists(in_container):
            in_container = Gentoo().local

        in_is_file = os.path.isfile(in_container)
        if in_is_file:
            in_container = setup_container(builddir, in_container)

        self._strategy.run(MockObj(builddir=builddir,
                                   in_container=in_container,
                                   out_container=out_container,
                                   mounts=mounts,
                                   shell=shell))
        clean_directories(builddir, in_is_file, True)


@Container.subcommand("bootstrap")
class ContainerBootstrap(cli.Application):
    """Check for the needed files."""

    def install_cmake_and_exit(self):
        """Tell the user to install cmake and aborts the current process."""
        print("You need to  install cmake via your package manager manually."
              " Exiting.")
        sys.exit(-1)

    def main(self, *args):
        print("Checking container binary dependencies...")
        if not find_package("uchroot"):
            if not find_package("cmake"):
                self.install_cmake_and_exit()
            install_uchroot()
        print("...OK")
        config_file = CFG["config_file"].value()
        if not (config_file and os.path.exists(config_file)):
            config_file = ".benchbuild.json"
        CFG.store(config_file)
        print("Storing config in {0}".format(os.path.abspath(config_file)))
        print(
            "Future container commands from this directory will automatically"
            " source the config file.")


@Container.subcommand("list")
class ContainerList(cli.Application):
    """Prints a list of the known containers."""

    def main(self, *args):
        containers = CFG["container"]["known"].value()
        for c in containers:
            print("[{1:.8s}] {0}".format(c["path"], str(c["hash"])))


def main(*args):
    return Container.run(*args)
