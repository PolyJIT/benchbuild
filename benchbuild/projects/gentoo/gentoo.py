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
import typing as tp

import attr
from plumbum import ProcessExecutionError, local
from plumbum.commands.base import BoundCommand

import benchbuild as bb
from benchbuild.environments.domain import declarative
from benchbuild.settings import CFG
from benchbuild.utils import compiler, container, path, run, uchroot
from benchbuild.utils.cmd import cp, ln
from benchbuild.utils.settings import Configuration

LOG = logging.getLogger(__name__)


@attr.s
class GentooGroup(bb.Project):
    """Gentoo ProjectGroup is the base class for every portage build."""

    GROUP = 'gentoo'
    SRC_FILE = None
    CONTAINER = declarative.ContainerImage().from_('benchbuild:alpine')

    emerge_env: tp.Dict[str, tp.Any] = attr.ib(
        default=attr.Factory(dict), repr=False, eq=False, order=False
    )

    def redirect(self) -> None:
        if not CFG["unionfs"]["enable"]:
            container.unpack(self.container, self.builddir)

        setup_networking()
        setup_benchbuild()
        configure_portage()

        self.configure_benchbuild(CFG)
        uchroot.mkfile_uchroot("/.benchbuild-container")
        benchbuild = find_benchbuild()
        _benchbuild = run.watch(benchbuild)
        with local.env(BB_VERBOSITY=str(CFG['verbosity'])):
            project_id = "{0}/{1}".format(self.name, self.group)
            _benchbuild("run", "-E", self.experiment.name, project_id)

    def compile(self) -> None:
        package_atom = "{domain}/{name}".format(
            domain=self.domain, name=self.name
        )

        LOG.debug('Installing dependencies.')
        emerge(package_atom, '--onlydeps', env=self.emerge_env)
        c_compiler = local.path(str(compiler.cc(self)))
        cxx_compiler = local.path(str(compiler.cxx(self)))

        setup_compilers('/etc/portage/make.conf')
        ln("-sf", str(c_compiler), local.path('/') / c_compiler.basename)
        ln('-sf', str(cxx_compiler), local.path('/') / cxx_compiler.basename)

        LOG.debug('Installing %s.', package_atom)
        emerge(package_atom, env=self.emerge_env)

    def configure_benchbuild(self, cfg: Configuration) -> None:
        config_file = local.path("/.benchbuild.yml")
        paths, libs = \
                uchroot.env(
                    uchroot.mounts(
                        "mnt",
                        cfg["container"]["mounts"].value))

        uchroot_cfg = cfg
        env = uchroot_cfg["env"].value
        env["PATH"] = paths
        env["LD_LIBRARY_PATH"] = libs

        uchroot_cfg["env"] = env
        uchroot_cfg['plugins']['projects'] = [str(self.__module__)]
        uchroot_cfg['plugins']['experiments'] = [
            str(self.experiment.__module__)
        ]
        uchroot_cfg["config_file"] = str(config_file)
        uchroot_cfg["unionfs"]["enable"] = False
        uchroot_cfg["build_dir"] = "/benchbuild/build"
        uchroot_cfg["tmp_dir"] = "/mnt/distfiles"
        uchroot_cfg["clean"] = False

        uchroot.mkfile_uchroot("/.benchbuild.yml")
        uchroot_cfg.store(".benchbuild.yml")

        write_sandbox_d("etc/sandbox.conf")


def emerge(package: str, *args: str, **env: str) -> None:
    from benchbuild.utils.cmd import emerge as gentoo_emerge

    with local.env(env):
        _emerge = run.watch(gentoo_emerge)
        _emerge("--autounmask-continue", args, package)


def setup_networking() -> None:
    LOG.debug("Setting up networking...")
    uchroot.mkfile_uchroot("/etc/resolv.conf")
    cp("/etc/resolv.conf", "etc/resolv.conf")
    write_wgetrc("etc/wgetrc")


def configure_portage() -> None:
    LOG.debug("Setting up Gentoo Portage...")
    write_makeconfig("etc/portage/make.conf")
    write_layout("etc/portage/metadata/layout.conf")
    write_bashrc("etc/portage/bashrc")


def write_sandbox_d(_path: str) -> None:
    uchroot.mkfile_uchroot(local.path('/') / _path)
    with open(_path, 'a') as sandbox_conf:
        lines = '''
SANDBOX_WRITE="/clang.stderr:/clang++.stderr:/clang.stdout:/clang++.stdout"
'''
        sandbox_conf.write(lines)


def setup_compilers(_path: str) -> None:
    LOG.debug("Arming compiler symlinks.")
    with open(_path, 'a') as makeconf:
        lines = '''
CC="/clang"
CXX="/clang++"
'''
        makeconf.write(lines)


def write_makeconfig(_path: str) -> None:
    """
    Write a valid gentoo make.conf file to :path:.

    Args:
        path - The output path of the make.conf
    """
    http_proxy = str(CFG["gentoo"]["http_proxy"])
    ftp_proxy = str(CFG["gentoo"]["ftp_proxy"])
    rsync_proxy = str(CFG["gentoo"]["rsync_proxy"])

    uchroot.mkfile_uchroot(local.path('/') / _path)
    with open(_path, 'w') as makeconf:
        lines = '''
PORTAGE_USERNAME=root
PORTAGE_GROUPNAME=root
CFLAGS="-O2 -pipe"
CXXFLAGS="${CFLAGS}"
FEATURES="nostrip -xattr"
CHOST="x86_64-pc-linux-gnu"
USE="bindist mmx sse sse2"
PORTDIR="/usr/portage"
DISTDIR="/mnt/distfiles"
PKGDIR="${PORTDIR}/packages"
'''

        makeconf.write(lines)

        mounts = CFG["container"]["mounts"].value
        tmp_dir = str(CFG["tmp_dir"])
        mounts.append({"src": tmp_dir, "tgt": "/mnt/distfiles"})
        CFG["container"]["mounts"] = mounts

        if http_proxy is not None:
            http_s = "http_proxy={0}".format(http_proxy)
            https_s = "https_proxy={0}".format(http_proxy)
            makeconf.write(http_s + "\n")
            makeconf.write(https_s + "\n")

        if ftp_proxy is not None:
            fp_s = "ftp_proxy={0}".format(ftp_proxy)
            makeconf.write(fp_s + "\n")

        if rsync_proxy is not None:
            rp_s = "RSYNC_PROXY={0}".format(rsync_proxy)
            makeconf.write(rp_s + "\n")


def write_bashrc(_path: str) -> None:
    """
    Write a valid gentoo bashrc file to :path:.

    Args:
        path - The output path of the make.conf
    """
    cfg_mounts = CFG["container"]["mounts"].value
    cfg_prefix = CFG["container"]["prefixes"].value

    uchroot.mkfile_uchroot("/etc/portage/bashrc")
    mounts = uchroot.mounts("mnt", cfg_mounts)
    p_paths, p_libs = uchroot.env(cfg_prefix)
    paths, libs = uchroot.env(mounts)

    paths = paths + p_paths
    libs = libs + p_libs

    with open(_path, 'w') as bashrc:
        lines = '''
export PATH="{0}:${{PATH}}"
export LD_LIBRARY_PATH="{1}:${{LD_LIBRARY_PATH}}"
'''.format(path.list_to_path(paths), path.list_to_path(libs))

        bashrc.write(lines)


def write_layout(_path: str) -> None:
    """
    Write a valid gentoo layout file to :path:.

    Args:
        path - The output path of the layout.conf
    """

    uchroot.mkdir_uchroot("/etc/portage/metadata")
    uchroot.mkfile_uchroot("/etc/portage/metadata/layout.conf")
    with open(_path, 'w') as layoutconf:
        lines = '''masters = gentoo'''
        layoutconf.write(lines)


def write_wgetrc(_path: str) -> None:
    """
    Write a valid gentoo wgetrc file to :path:.

    Args:
        path - The output path of the wgetrc
    """
    http_proxy = str(CFG["gentoo"]["http_proxy"])
    ftp_proxy = str(CFG["gentoo"]["ftp_proxy"])

    uchroot.mkfile_uchroot("/etc/wgetrc")
    with open(_path, 'w') as wgetrc:
        if http_proxy is not None:
            http_s = "http_proxy = {0}".format(http_proxy)
            https_s = "https_proxy = {0}".format(http_proxy)
            wgetrc.write("use_proxy = on\n")
            wgetrc.write(http_s + "\n")
            wgetrc.write(https_s + "\n")

        if ftp_proxy is not None:
            fp_s = "ftp_proxy={0}".format(ftp_proxy)
            wgetrc.write(fp_s + "\n")


def setup_virtualenv(_path: str = "/benchbuild") -> None:
    LOG.debug("Setting up Benchbuild virtualenv...")
    env = uchroot.uchroot()["/usr/bin/env"]
    env = env['-i', '--']
    venv = env["/usr/bin/virtualenv"]
    venv = venv("-p", "/usr/bin/python3", _path)


def find_benchbuild() -> tp.Optional[BoundCommand]:
    try:
        uchrt = uchroot.clean_env(uchroot.uchroot(), ['HOME'])
        benchbuild_loc = uchrt("which", "benchbuild").strip()
        benchbuild = uchrt[benchbuild_loc]
        return benchbuild
    except ProcessExecutionError as err:
        LOG.error("Could not find Benchbuild inside container")
        LOG.debug("Reason: %s", str(err))
    return None


def requires_update(benchbuild: BoundCommand) -> bool:
    try:
        c_version = benchbuild("--version").strip().split()[-1]
        h_version = str(CFG["version"])

        LOG.debug("container: %s", c_version)
        LOG.debug("host: %s", h_version)
        if c_version == h_version:
            return False
    except ProcessExecutionError as err:
        LOG.error("Querying Benchbuild inside container failed")
        LOG.debug("Reason: %s", str(err))
    return True


def setup_benchbuild() -> None:
    """
    Setup benchbuild inside a container.

    This will query a for an existing installation of benchbuild and
    try to upgrade it to the latest version, if possible.
    """
    LOG.debug("Setting up Benchbuild...")

    venv_dir = local.path("/benchbuild")
    prefixes = CFG["container"]["prefixes"].value
    prefixes.append(venv_dir)
    CFG["container"]["prefixes"] = prefixes

    src_dir = str(CFG["source_dir"])
    have_src = src_dir is not None
    if have_src:
        __mount_source(src_dir)

    benchbuild = find_benchbuild()
    if benchbuild and not requires_update(benchbuild):
        if have_src:
            __upgrade_from_source(venv_dir, with_deps=False)
        return

    setup_virtualenv(venv_dir)
    if have_src:
        __upgrade_from_source(venv_dir)
    else:
        __upgrade_from_pip(venv_dir)


def __upgrade_from_pip(venv_dir: local.path) -> None:
    LOG.debug("Upgrading from pip")
    uchrt_cmd = uchroot.clean_env(uchroot.uchroot(), ['HOME'])
    uchroot.uretry(
        uchrt_cmd[venv_dir / "bin" / "pip3", "install", "--upgrade",
                  "benchbuild"]
    )


def __mount_source(src_dir: str) -> None:
    src_dir = local.path(str(src_dir))
    mounts = CFG["container"]["mounts"].value
    mount = {"src": src_dir, "tgt": "/mnt/benchbuild"}
    mounts.append(mount)
    CFG["container"]["mounts"] = mounts


def __upgrade_from_source(venv_dir: local.path, with_deps: bool = True) -> None:
    LOG.debug("Upgrading from source")
    uchrt_cmd = uchroot.clean_env(uchroot.uchroot(), ['HOME'])
    opts = ["--upgrade"]
    if not with_deps:
        opts.append("--no-deps")

    uchrt_cmd = uchrt_cmd[venv_dir / "bin" / "pip3", "install"]
    uchrt_cmd = uchrt_cmd[opts]
    uchrt_cmd = uchrt_cmd["/mnt/benchbuild"]

    uchroot.uretry(uchrt_cmd)
