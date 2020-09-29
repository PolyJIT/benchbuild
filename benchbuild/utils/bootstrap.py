""" Helper functions for bootstrapping external dependencies. """
import logging
import os
import platform
import sys
import typing as tp
from getpass import getuser

from plumbum import FG, TF, ProcessExecutionError, local

from benchbuild import settings, utils
from benchbuild.utils import user_interface as ui
from benchbuild.utils.cmd import cmake, git, grep, make

CFG = settings.CFG
LOG = logging.getLogger(__name__)


def find_package(binary: str) -> bool:
    """
    Find the binary as a usable python object in the system.

    Args:
        binary: The binary name to look for.

    Returns:
        True, if the binary name can be imported by benchbuild.
    """
    from benchbuild.utils import cmd
    c = cmd.__getattr__(binary)

    found = not isinstance(c, utils.ErrorCommand)
    if found:
        print("Checking for {} - Yes [{}]".format(binary, str(c)))
    else:
        print("Checking for {}  - No".format(binary))

    return found


PACKAGES = {
    "unionfs": {
        "gentoo base system": ["sys-fs/unionfs-fuse"],
        "ubuntu": ["unionfs-fuse"],
        "debian": ["unionfs-fuse"],
        "suse": ["unionfs-fuse"]
    },
    "postgres": {
        "gentoo base system": ["dev-db/postgres", "dev-libs/libpqxx"],
        "ubuntu": ["libpq-dev", "libpqxx-dev"],
        "debian": ["libpq-dev", "libpqxx-dev"],
        "suse": ["postgresql-devel", "libpqxx-devel"]
    },
    "fusermount": {
        "gentoo base system": ["sys-fs/fuse"],
        "ubuntu": ["fuse"],
        "debian": ["fuse"],
        "suse": ["fuse", "fuse-devel"]
    },
    "cmake": {
        "gentoo base system": ["dev-util/cmake"],
        "ubuntu": ["cmake"],
        "debian": ["cmake"],
        "suse": ["cmake"]
    },
    "autoreconf": {
        "ubuntu": ["autoconf"],
        "debian": ["autoconf"],
        "suse": ["autoconf"]
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
    },
    "suse": {
        "cmd": "zypper",
        "args": ["install"],
    }
}


def install_uchroot(_):
    """Installer for erlent (contains uchroot)."""
    builddir = local.path(str(CFG["build_dir"].value))
    with local.cwd(builddir):
        erlent_src = local.path('erlent')
        erlent_git = erlent_src / '.git'
        erlent_repo = str(CFG['uchroot']['repo'])
        erlent_build = erlent_src / 'build'
        if not erlent_git.exists():
            git("clone", erlent_repo)
        else:
            with local.cwd(erlent_src):
                git("pull", "--rebase")

        erlent_build.mkdir()
        with local.cwd(erlent_build):
            cmake("../")
            make()

    os.environ["PATH"] = os.path.pathsep.join([
        erlent_build, os.environ["PATH"]
    ])
    local.env.update(PATH=os.environ["PATH"])

    if not find_package("uchroot"):
        LOG.error(
            'uchroot not found, after updating PATH to %s', os.environ['PATH']
        )
        sys.exit(-1)

    env = CFG['env'].value
    if 'PATH' not in env:
        env['PATH'] = []
    env['PATH'].append(str(erlent_build))


def check_uchroot_config() -> None:
    """
    Check, if the configuration of uchroot is valid for benchbuild.
    """
    print("Checking configuration of 'uchroot'")

    fuse_grep = grep['-q', '-e']
    username = getuser()

    if not (fuse_grep["^user_allow_other", "/etc/fuse.conf"] & TF):
        print("uchroot needs 'user_allow_other' enabled in '/etc/fuse.conf'.")
    if not (fuse_grep["^{0}".format(username), "/etc/subuid"] & TF):
        print(
            "uchroot needs an entry for user '{0}' in '/etc/subuid'.".
            format(username)
        )
    if not (fuse_grep["^{0}".format(username), "/etc/subgid"] & TF):
        print(
            "uchroot needs an entry for user '{0}' in '/etc/subgid'.".
            format(username)
        )


def linux_distribution_major() -> tp.Optional[str]:
    """
    Get the used linux distribution.

    Returns:
        The name of the linux distribution, if known.
    """
    if not platform.system() == 'Linux':
        return None

    # python > 3.7
    lsb_release = local["lsb_release"]
    distribution = lsb_release["-ds"]().strip().lower()
    known_distributions = ["suse", "debian", "ubuntu", "gentoo"]

    for known in known_distributions:
        if known in distribution:
            return known

    return None


def install_package(pkg_name: str) -> bool:
    """
    Install the given package.

    This makes use of the systems package manager, if known.

    Args:
        pkg_name: The package name to install.
    """
    if not bool(CFG['bootstrap']['install']):
        return False

    if pkg_name not in PACKAGES:
        print("No bootstrap support for package '{0}'".format(pkg_name))
    linux = linux_distribution_major()
    package_manager = PACKAGE_MANAGER[linux]
    packages = PACKAGES[pkg_name][linux]
    for pkg_name_on_host in packages:
        print("You are missing the package: '{0}'".format(pkg_name_on_host))
        cmd = local["sudo"]
        cmd = cmd[package_manager["cmd"], package_manager["args"],
                  pkg_name_on_host]
        cmd_str = str(cmd)

        ret = False
        if ui.ask("Run '{cmd}' to install it?".format(cmd=cmd_str)):
            print("Running: '{cmd}'".format(cmd=cmd_str))

        try:
            (cmd & FG(retcode=0))
        except ProcessExecutionError:
            print("NOT INSTALLED")
        else:
            print("OK")
    return ret


def provide_package(
    pkg_name: str,
    installer: tp.Callable[[str], bool] = install_package
) -> None:
    """
    Make sure the package is provided by the system, if required.

    Args:
        pkg_name: The package name to provide.
        installer: An installer function that is used,
            if the package needs to be installed.
    """
    if not find_package(pkg_name):
        installer(pkg_name)


def provide_packages(pkg_names: tp.List[str]) -> None:
    """
    Provide all given packages in the system.

    Args:
        pkg_names: A list of package names to provide in the system.
    """
    for pkg_name in pkg_names:
        provide_package(pkg_name)
