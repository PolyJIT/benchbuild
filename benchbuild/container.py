#!/usr/bin/env python3

from plumbum import cli, local, TF, FG, ProcessExecutionError
from benchbuild.utils.cmd import tar, mkdir, mv, rm, bash
from benchbuild import settings
from benchbuild.utils import log
from benchbuild.utils.bootstrap import find_package, install_uchroot
from benchbuild.utils.run import run, uchroot, uchroot_no_args
from benchbuild.utils.downloader import Copy, update_hash
from benchbuild.utils.user_interface import ask
from abc import abstractmethod
import logging
import sys
import os


def clean_directories(builddir, in_dir=True, out_dir=True):
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
    with local.cwd(builddir):
        if not os.path.exists("container-in"):
            mkdir("-p", "container-in")
        if not os.path.exists("container-out"):
            mkdir("-p", "container-out")


def setup_container(builddir, container):
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
    uchroot = uchroot_no_args()["-E", "-A", "-u", "0", "-g", "0", "-C", "-w",
                                "/", "-r", os.path.abspath(container_dir)]
    uchroot_m = uchroot
    uchroot = uchroot["--"]

    for mount in mounts:
        absdir = os.path.abspath(str(mount))
        dirname = os.path.split(absdir)[-1]
        uchroot_m = uchroot_m["-M", "{0}:/mnt/{1}".format(absdir, dirname)]
        mount_path = os.path.join(container_dir, "mnt", dirname)
        if not os.path.exists(mount_path):
            uchroot("mkdir", "-p", "/mnt/{0}".format(dirname))
        print("Mounting: '{0}' inside container at '/mnt/{1}'".format(mount,
                                                                      dirname))

    cmd_path = os.path.join(container_dir, command[0].lstrip('/'))
    if not os.path.exists(cmd_path):
        logging.error(
            "The command does not exist inside the container! {0}".format(
                cmd_path))
        return

    cmd = uchroot_m[command]
    return cmd & FG


def setup_bash_in_container(builddir, container, outfile, mounts, shell):
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

            container_filename = os.path.split(container)[-1]
            container_out = os.path.join("container-out", container_filename)
            container_out = os.path.abspath(container_out)

            # Pack the results to: container-out
            with local.cwd("container-in"):
                tar("cjf", container_out, ".")
            c_hash = update_hash(container_filename,
                                 os.path.dirname(container_out))
            outdir = os.path.dirname(outfile)
            if not os.path.exists(outdir):
                mkdir("-p", outdir)
            mv(container_out, outfile)

            new_container = {"path": outfile, "hash": str(c_hash)}
            config_path = settings.CFG["config_file"].value()
            settings.CFG["container"]["known"].value().append(new_container)
            settings.CFG.store(config_path)
            print("Storing config in {0}".format(os.path.abspath(config_path)))


def find_hash(container_db, key):
    for kv in container_db:
        if kv["hash"].startswith(key):
            return kv["path"]
    return None


def set_input_container(container, cfg):
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
    @abstractmethod
    def run(self, context):
        pass


class BashStrategy(ContainerStrategy):
    def run(self, context):
        setup_bash_in_container(context.builddir, context.in_container,
                                context.out_container, context.mounts,
                                context.shell)


class SetupPolyJITGentooStrategy(ContainerStrategy):
    def run(self, context):
        """
        Setup a gentoo container suitable for PolyJIT.


        """
        import sys
        # Don't do something when running non-interactive.
        if not sys.stdout.isatty():
            return

        with local.cwd(context.container_root):
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


class Container(cli.Application):
    """Manage uchroot containers."""
    VERSION = settings.CFG["version"].value()

    def __init__(self, exe):
        super(Container, self).__init__(exe)

    @cli.switch(["-i", "--input-file"], str, help="Input container path")
    def input_file(self, container):
        p = os.path.abspath(container)
        if set_input_container(p, settings.CFG):
            return

        p = find_hash(settings.CFG["container"]["known"].value(), container)
        if set_input_container(p, settings.CFG):
            return

        raise ValueError("The path '{0}' does not exist.".format(p))

    @cli.switch(["-o", "--output-file"], str, help="Output container path")
    def output_file(self, container):
        p = os.path.abspath(container)
        if os.path.exists(p):
            if not ask("Path '{0}' already exists." " Overwrite?".format(p)):
                sys.exit(0)
        settings.CFG["container"]["output"] = p

    @cli.switch(["-s", "--shell"],
                str,
                help="The shell command we invoke inside the container.")
    def shell(self, custom_shell):
        settings.CFG["container"]["shell"] = custom_shell

    @cli.switch(["-t", "-tmp-dir"],
                cli.ExistingDirectory,
                help="Temporary directory")
    def builddir(self, tmpdir):
        settings.CFG["build_dir"] = tmpdir

    @cli.switch(
        ["m", "--mount"],
        cli.ExistingDirectory,
        list=True,
        help="Mount the given directory under / inside the uchroot container")
    def mounts(self, user_mount):
        settings.CFG["container"]["mounts"] = user_mount

    verbosity = cli.CountOf('-v', help="Enable verbose output")

    def main(self, *args):

        log.configure()
        LOG = logging.getLogger()
        LOG.setLevel({
            3: logging.DEBUG,
            2: logging.INFO,
            1: logging.WARNING,
            0: logging.ERROR
        }[self.verbosity])

        settings.update_env()
        builddir = os.path.abspath(str(settings.CFG["build_dir"].value()))
        if not os.path.exists(builddir):
            response = ask("The build directory {dirname} does not exist yet. "
                           "Should I create it?".format(dirname=builddir))

            if response:
                mkdir("-p", builddir)
                print("Created directory {0}.".format(builddir))

        setup_directories(builddir)


@Container.subcommand("run")
class ContainerRun(cli.Application):
    def main(self, *args):
        builddir = settings.CFG["build_dir"].value()
        in_container = settings.CFG["container"]["input"].value()
        mounts = settings.CFG["container"]["mounts"].value()
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

    We offer a variety of creation policies for a new container. By default
    a basic 'spawn a bash' policy is used. This just leaves you inside a bash
    that is started in the extracted container. After customization you can exit
    the bash and pack up the result.
    """

    strategy = BashStrategy()

    @cli.switch(["-S", "--strategy"],
                cli.Set("bash", "polyjit", case_sensitive=False),
                help="Defines the strategy used to create a new container.",
                mandatory=False)
    def strategy(self, strategy):
        self.strategy = {
            "bash": BashStrategy(),
            "polyjit": SetupPolyJITGentooStrategy()
        }[strategy]

    def main(self, *args):
        builddir = settings.CFG["build_dir"].value()
        in_container = settings.CFG["container"]["input"].value()
        out_container = settings.CFG["container"]["output"].value()
        mounts = settings.CFG["container"]["mounts"].value()
        shell = settings.CFG["container"]["shell"].value()
        in_is_file = os.path.isfile(in_container)
        if in_is_file:
            in_container = setup_container(builddir, in_container)

        self.strategy.run(MockObj(builddir=builddir,
                                  in_container=in_container,
                                  out_container=out_container,
                                  mounts=mounts,
                                  shell=shell))
        clean_directories(builddir, in_is_file, True)


@Container.subcommand("bootstrap")
class ContainerBootstrap(cli.Application):
    def install_cmake_and_exit(self):
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
        config_file = settings.CFG["config_file"].value()
        if not (config_file and os.path.exists(config_file)):
            config_file = ".benchbuild.json"
        settings.CFG.store(config_file)
        print("Storing config in {0}".format(os.path.abspath(config_file)))
        print(
            "Future container commands from this directory will automatically"
            " source the config file.")


@Container.subcommand("list")
class ContainerList(cli.Application):
    def main(self, *args):
        containers = settings.CFG["container"]["known"].value()
        for c in containers:
            print("[{1:.8s}] {0}".format(c["path"], str(c["hash"])))


def main(*args):
    return Container.run(*args)
