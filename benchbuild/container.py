"""
Container construction tool.

This tool assists in the creation of customized uchroot containers.
You can define strategies and apply them on a given container base-image
to have a fixed way of creating a user-space environment.
"""
import logging
import os
import sys
from abc import abstractmethod

from plumbum import FG, TF, ProcessExecutionError, cli, local

from benchbuild.settings import CFG
from benchbuild.utils import bootstrap, container, download, log, run, uchroot
from benchbuild.utils import user_interface as ui
from benchbuild.utils.cmd import bash, mkdir, mv, rm, tar
from benchbuild.utils.settings import get_number_of_jobs

LOG = logging.getLogger(__name__)


def clean_directories(builddir, in_dir=True, out_dir=True):
    """Remove the in and out of the container if confirmed by the user."""
    container_in = local.path(builddir) / "container-in"
    container_out = local.path(builddir) / "container-out"

    if in_dir and container_in.exists():
        if ui.ask("Should I delete '{0}'?".format(container_in)):
            container_in.delete()
    if out_dir and container_out.exists():
        if ui.ask("Should I delete '{0}'?".format(container_out)):
            container_out.delete()


def setup_directories(builddir):
    """Create the in and out directories of the container."""
    build_dir = local.path(builddir)
    in_dir = build_dir / "container-in"
    out_dir = build_dir / "container-out"

    if not in_dir.exists():
        in_dir.mkdir()
    if not out_dir.exists():
        out_dir.mkdir()


def setup_container(builddir, _container):
    """Prepare the container and returns the path where it can be found."""
    build_dir = local.path(builddir)
    in_dir = build_dir / "container-in"
    container_path = local.path(_container)
    with local.cwd(builddir):
        container_bin = container_path.basename
        container_in = in_dir / container_bin
        download.Copy(_container, container_in)
        uchrt = uchroot.no_args()

        with local.cwd("container-in"):
            uchrt = uchrt["-E", "-A", "-u", "0", "-g", "0", "-C", "-r", "/",
                          "-w",
                          os.path.abspath("."), "--"]

        # Check, if we need erlent support for this archive.
        has_erlent = bash["-c",
                          "tar --list -f './{0}' | grep --silent '.erlent'".
                          format(container_in)]
        has_erlent = (has_erlent & TF)

        # Unpack input container to: container-in
        if not has_erlent:
            cmd = local["/bin/tar"]["xf"]
            cmd = uchrt[cmd[container_bin]]
        else:
            cmd = tar["xf"]
            cmd = cmd[container_in]

        with local.cwd("container-in"):
            cmd("--exclude=dev/*")
        rm(container_in)
    return in_dir


def run_in_container(command, container_dir):
    """
    Run a given command inside a container.

    Mounts a directory as a container at the given mountpoint and tries to run
    the given command inside the new container.
    """
    container_p = local.path(container_dir)
    with local.cwd(container_p):
        uchrt = uchroot.with_mounts()
        uchrt = uchrt["-E", "-A", "-u", "0", "-g", "0", "-C", "-w", "/", "-r",
                      container_p]
        uchrt = uchrt["--"]

        cmd_path = container_p / command[0].lstrip('/')
        if not cmd_path.exists():
            LOG.error(
                "The command does not exist inside the container! %s", cmd_path
            )
            raise ValueError('The command does not exist inside the container!')

        cmd = uchrt[command]
        return cmd & FG


def pack_container(in_container, out_file):
    """
    Pack a container image into a .tar.bz2 archive.

    Args:
        in_container (str): Path string to the container image.
        out_file (str): Output file name.
    """
    container_filename = local.path(out_file).basename
    out_container = local.cwd / "container-out" / container_filename
    out_dir = out_container.dirname

    # Pack the results to: container-out
    with local.cwd(in_container):
        tar("cjf", out_container, ".")
    c_hash = download.update_hash(out_container)
    if out_dir.exists():
        mkdir("-p", out_dir)
    mv(out_container, out_file)
    mv(out_container + ".hash", out_file + ".hash")

    new_container = {"path": out_file, "hash": str(c_hash)}
    CFG["container"]["known"] += new_container


def setup_bash_in_container(builddir, _container, outfile, shell):
    """
    Setup a bash environment inside a container.

    Creates a new chroot, which the user can use as a bash to run the wanted
    projects inside the mounted container, that also gets returned afterwards.
    """
    with local.cwd(builddir):
        # Switch to bash inside uchroot
        print(
            "Entering bash inside User-Chroot. Prepare your image and "
            "type 'exit' when you are done. If bash exits with a non-zero"
            "exit code, no new container will be stored."
        )
        store_new_container = True
        try:
            run_in_container(shell, _container)
        except ProcessExecutionError:
            store_new_container = False

        if store_new_container:
            print("Packing new container image.")
            pack_container(_container, outfile)
            config_path = str(CFG["config_file"])
            CFG.store(config_path)
            print("Storing config in {0}".format(os.path.abspath(config_path)))


def find_hash(container_db, key):
    """Find the first container in the database with the given key."""
    for keyvalue in container_db:
        if keyvalue["hash"].startswith(key):
            return keyvalue["path"]
    return None


def set_input_container(_container, cfg):
    """Save the input for the container in the configurations."""
    if not _container:
        return False
    if _container.exists():
        cfg["container"]["input"] = str(_container)
        return True
    return False


class MockObj:
    """Context object to be used in strategies.

    This object's attributes are initialized on construction.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ContainerStrategy:
    """Interfaces for the different containers chosen by the experiment."""

    @abstractmethod
    def run(self, context):
        """Execute a container strategy.

        Args:
            context: A context object with attributes used for the strategy.
        """


class BashStrategy(ContainerStrategy):
    """The user interface for setting up a bash inside the container."""

    def run(self, context):
        print(
            "Entering a shell in the container.\nUse the exit "
            "command to leave the container."
        )
        setup_bash_in_container(
            context.builddir, context.in_container, context.out_container,
            context.shell
        )


class SetupPolyJITGentooStrategy(ContainerStrategy):
    """Interface of using gentoo as a container for an experiment."""

    def run(self, context):
        """Setup a gentoo container suitable for PolyJIT."""
        # Don't do something when running non-interactive.
        if not sys.stdout.isatty():
            return

        with local.cwd(context.in_container):
            from benchbuild.projects.gentoo import gentoo
            gentoo.setup_networking()
            gentoo.configure_portage()

            sed_in_chroot = uchroot.uchroot()["/bin/sed"]
            sed_in_chroot = run.watch(sed_in_chroot)
            emerge_in_chroot = uchroot.uchroot()["/usr/bin/emerge"]
            emerge_in_chroot = run.watch(emerge_in_chroot)
            has_pkg = uchroot.uchroot()["/usr/bin/qlist", "-I"]

            sed_in_chroot("-i", '/CC=/d', "/etc/portage/make.conf")
            sed_in_chroot("-i", '/CXX=/d', "/etc/portage/make.conf")

            want_sync = bool(CFG["container"]["strategy"]["polyjit"]["sync"])
            want_upgrade = bool(
                CFG["container"]["strategy"]["polyjit"]["upgrade"]
            )

            packages = \
                CFG["container"]["strategy"]["polyjit"]["packages"].value
            with local.env(MAKEOPTS="-j{0}".format(get_number_of_jobs(CFG))):
                if want_sync:
                    LOG.debug("Synchronizing portage.")
                    emerge_in_chroot("--sync")
                if want_upgrade:
                    LOG.debug("Upgrading world.")
                    emerge_in_chroot(
                        "--autounmask-only=y", "-uUDN", "--with-bdeps=y",
                        "@world"
                    )
                for pkg in packages:
                    if has_pkg[pkg["name"]] & TF:
                        continue
                    env = pkg["env"]
                    with local.env(**env):
                        emerge_in_chroot(pkg["name"])

            gentoo.setup_benchbuild()

        print("Packing new container image.")
        with local.cwd(context.builddir):
            pack_container(context.in_container, context.out_container)


class Container(cli.Application):
    """Manage uchroot containers."""

    VERSION = str(CFG["version"])

    @cli.switch(["-i", "--input-file"], str, help="Input container path")
    def input_file(self, _container):
        """Find the input path of a uchroot container."""
        p = local.path(_container)
        if set_input_container(p, CFG):
            return

        p = find_hash(CFG["container"]["known"].value, container)
        if set_input_container(p, CFG):
            return

        raise ValueError("The path '{0}' does not exist.".format(p))

    @cli.switch(["-o", "--output-file"], str, help="Output container path")
    def output_file(self, _container):
        """Find and writes the output path of a chroot container."""
        p = local.path(_container)
        if p.exists():
            if not ui.ask("Path '{0}' already exists." " Overwrite?".format(p)):
                sys.exit(0)
        CFG["container"]["output"] = str(p)

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
        help="Mount the given directory under / inside the uchroot container"
    )
    def mounts(self, user_mount):
        """Save the current mount of the container into the settings."""
        CFG["container"]["mounts"] = user_mount

    verbosity = cli.CountOf('-v', help="Enable verbose output")

    def main(self, *args):
        log.configure()
        builddir = local.path(str(CFG["build_dir"]))
        if not builddir.exists():
            response = ui.ask(
                "The build directory {dirname} does not exist yet. "
                "Should I create it?".format(dirname=builddir)
            )

            if response:
                mkdir("-p", builddir)
                print("Created directory {0}.".format(builddir))

        setup_directories(builddir)


@Container.subcommand("run")
class ContainerRun(cli.Application):
    """Execute commannds inside a prebuilt container."""

    def main(self, *args):
        builddir = str(CFG["build_dir"])
        in_container = str(CFG["container"]["input"])

        if (in_container is None) or not os.path.exists(in_container):
            in_is_file = False
            in_container = container.Gentoo().local
        else:
            in_is_file = os.path.isfile(in_container)
            if in_is_file:
                clean_directories(builddir)
                setup_directories(builddir)
                in_container = setup_container(builddir, in_container)

        run_in_container(args, in_container)
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
        """Select strategy based on key.

        Args:
            strategy (str): The strategy to select.

        Returns:
            A strategy object.
        """
        self._strategy = {
            "bash": BashStrategy(),
            "polyjit": SetupPolyJITGentooStrategy()
        }[strategy]

    def main(self, *args):
        builddir = str(CFG["build_dir"])
        in_container = str(CFG["container"]["input"])
        out_container = str(CFG["container"]["output"])
        mounts = CFG["container"]["mounts"].value
        shell = str(CFG["container"]["shell"])

        if (in_container is None) or not os.path.exists(in_container):
            in_container = container.Gentoo().local

        in_is_file = os.path.isfile(in_container)
        if in_is_file:
            in_container = setup_container(builddir, in_container)

        self._strategy.run(
            MockObj(
                builddir=builddir,
                in_container=in_container,
                out_container=out_container,
                mounts=mounts,
                shell=shell
            )
        )
        clean_directories(builddir, in_is_file, True)


@Container.subcommand("bootstrap")
class ContainerBootstrap(cli.Application):
    """Check for the needed files."""

    def install_cmake_and_exit(self):
        """Tell the user to install cmake and aborts the current process."""
        print(
            "You need to  install cmake via your package manager manually."
            " Exiting."
        )
        sys.exit(-1)

    def main(self, *args):
        print("Checking container binary dependencies...")
        if not bootstrap.find_package("uchroot"):
            if not bootstrap.find_package("cmake"):
                self.install_cmake_and_exit()
            bootstrap.install_uchroot(None)
        print("...OK")
        config_file = str(CFG["config_file"])
        if not (config_file and os.path.exists(config_file)):
            config_file = ".benchbuild.json"
        CFG.store(config_file)
        print("Storing config in {0}".format(os.path.abspath(config_file)))
        print(
            "Future container commands from this directory will automatically"
            " source the config file."
        )


@Container.subcommand("list")
class ContainerList(cli.Application):
    """Prints a list of the known containers."""

    def main(self, *args):
        containers = CFG["container"]["known"].value
        for c in containers:
            print("[{1:.8s}] {0}".format(c["path"], str(c["hash"])))


def main(*args):
    """Main entry point for the container tool."""
    return Container.run(*args)
