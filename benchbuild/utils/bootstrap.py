""" Helper functions for bootstrapping external dependencies. """
import benchbuild.utils.user_interface as ui
import platform
import os
import sys
from plumbum import local, TF
from benchbuild import settings

ask = ui.ask


def find_package(binary):
    try:
        from benchbuild.utils import cmd
        c = cmd.__getattr__(binary)
        print("Checking for {} - Yes [{}]".format(binary, str(c)))
    except AttributeError:
        print("Checking for {}  - No".format(binary))
        return False
    return True


PACKAGES = {
    "unionfs": {
        "gentoo base system": ["sys-fs/unionfs-fuse"],
        "ubuntu": ["unionfs-fuse"],
        "debian": ["unionfs-fuse"]
    },
    "postgres": {
        "gentoo base system": ["dev-db/postgres", "dev-libs/libpqxx"],
        "ubuntu": ["libpq-dev", "libpqxx-dev"],
        "debian": ["libpq-dev", "libpqxx-dev"]
    },
    "fusermount": {
        "gentoo base system": ["sys-fs/fuse"],
        "ubuntu": ["fuse"],
        "debian": ["fuse"]
    }
}

PACKAGE_MANAGER = {
    "gentoo base system": {
        "cmd": "emerge",
        "args": ["-a"]
    },
    "ubuntu": {
        "cmd": "apt-get",
        "args": ["install"]
    },
    "debian": {
        "cmd": "apt-get",
        "args": ["install"]
    }
}


def install_uchroot():
    from benchbuild.utils.cmd import git, mkdir
    builddir = settings.CFG["build_dir"].value()
    with local.cwd(builddir):
        if not os.path.exists("erlent/.git"):
            git("clone", settings.CFG["uchroot"]["repo"].value())
        else:
            with local.cwd("erlent"):
                git("pull", "--rebase")
        mkdir("-p", "erlent/build")
        with local.cwd("erlent/build"):
            from benchbuild.utils.cmd import cmake
            from benchbuild.utils.cmd import make
            cmake("../")
            make()
    erlent_path = os.path.abspath(os.path.join(builddir, "erlent", "build"))
    os.environ["PATH"] = os.path.pathsep.join([erlent_path, os.environ[
        "PATH"]])
    local.env.update(PATH=os.environ["PATH"])
    if not find_package("uchroot"):
        sys.exit(-1)
    settings.CFG["env"]["path"].value().append(erlent_path)


def check_uchroot_config():
    from benchbuild.utils.cmd import grep
    from getpass import getuser
    print("Checking configuration of 'uchroot'")

    fuse_grep = grep["-q", '-e']
    username = getuser()

    if not (fuse_grep["^user_allow_other", "/etc/fuse.conf"] & TF):
        print("uchroot needs 'user_allow_other' enabled in '/etc/fuse.conf'.")
    if not (fuse_grep["^{0}".format(username), "/etc/subuid"] & TF):
        print("uchroot needs an entry for user '{0}' in '/etc/subuid'.".format(
            username))
    if not (fuse_grep["^{0}".format(username), "/etc/subgid"] & TF):
        print("uchroot needs an entry for user '{0}' in '/etc/subgid'.".format(
            username))


def linux_distribution_major():
    if not platform.system() == 'Linux':
        return None

    return platform.linux_distribution()


def install_package(pkg_name):
    if pkg_name not in PACKAGES:
        print("No bootstrap support for package '{0}'".format(pkg_name))
    linux, _, _ = linux_distribution_major()
    linux = str(linux.lower())
    package_manager = PACKAGE_MANAGER[linux]
    packages = PACKAGES[pkg_name][linux]
    for pkg_name_on_host in packages:
        print("You are missing the package: '{0}'".format(pkg_name_on_host))
        cmd = local["sudo"]
        cmd = cmd[package_manager["cmd"],
                  package_manager["args"],
                  pkg_name_on_host]
        cmd_str = str(cmd)

        ret = False
        if ask("Run '{cmd}' to install it?".format(cmd=cmd_str)):
            print("Running: '{cmd}'".format(cmd=cmd_str))
            ret = (cmd & TF(retcode=0))
        if ret:
            print("OK")
        else:
            print("NOT INSTALLED")
    return ret


def provide_package(pkg_name):
    if not find_package(pkg_name):
        install_package(pkg_name)


def provide_packages(pkg_names):
    for pkg_name in pkg_names:
        provide_package(pkg_name)
