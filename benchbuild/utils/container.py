"""Container utilites."""
import logging
import os
from datetime import datetime

from plumbum import TF, ProcessExecutionError, local

from benchbuild.settings import CFG
from benchbuild.utils.cmd import awk, bash, cp, curl, cut, rm, tail
from benchbuild.utils.download import Wget

LOG = logging.getLogger(__name__)


def cached(func):
    """Memoize a function result."""
    ret = None

    def call_or_cache(*args, **kwargs):
        nonlocal ret
        if ret is None:
            ret = func(*args, **kwargs)
        return ret

    return call_or_cache


class Container:
    name = "container"

    @property
    def remote(self):
        pass

    @property
    def filename(self):
        image_cfg = CFG["container"]["images"].value
        image_cfg = image_cfg[self.name]
        tmp_dir = local.path(str(CFG["tmp_dir"]))

        if os.path.isabs(image_cfg):
            return image_cfg
        return tmp_dir / image_cfg

    @property
    def local(self):
        """
        Finds the current location of a container.
        Also unpacks the project if necessary.

        Returns:
            target: The path, where the container lies in the end.
        """
        assert self.name in CFG["container"]["images"].value
        tmp_dir = local.path(str(CFG["tmp_dir"]))
        target_dir = tmp_dir / self.name

        if not target_dir.exists() or not is_valid(self, target_dir):
            unpack(self, target_dir)

        return target_dir


class Gentoo(Container):
    name = "gentoo"
    _LATEST_TXT = \
        "http://distfiles.gentoo.org/releases/amd64/autobuilds/"\
        "latest-stage3-amd64.txt"

    @property
    @cached
    def src_file(self):
        """
        Get the latest src_uri for a stage 3 tarball.

        Returns (str):
            Latest src_uri from gentoo's distfiles mirror.
        """
        try:
            src_uri = (curl[Gentoo._LATEST_TXT] | tail["-n", "+3"] |
                       cut["-f1", "-d "])().strip()
        except ProcessExecutionError as proc_ex:
            src_uri = "NOT-FOUND"
            LOG.error("Could not determine latest stage3 src uri: %s",
                      str(proc_ex))
        return src_uri

    @property
    @cached
    def version(self):
        """Return the build date of the gentoo container."""
        try:
            _version = (curl[Gentoo._LATEST_TXT] | \
                    awk['NR==2{print}'] | \
                    cut["-f2", "-d="])().strip()
            _version = datetime.utcfromtimestamp(int(_version))\
                .strftime("%Y-%m-%d")
        except ProcessExecutionError as proc_ex:
            _version = "unknown"
            LOG.error("Could not determine timestamp: %s", str(proc_ex))
        return _version

    @property
    def remote(self):
        """Get a remote URL of the requested container."""
        return "http://distfiles.gentoo.org/releases/amd64/autobuilds/{0}" \
            .format(self.src_file)


def is_valid(container, path):
    """
    Checks if a container exists and is unpacked.

    Args:
        path: The location where the container is expected.

    Returns:
        True if the container is valid, False if the container needs to
        unpacked or if the path does not exist yet.
    """
    try:
        tmp_hash_path = container.filename + ".hash"
        with open(tmp_hash_path, 'r') as tmp_file:
            tmp_hash = tmp_file.readline()
    except IOError:
        LOG.info("No .hash-file in the tmp-directory.")

    container_hash_path = local.path(path) / "gentoo.tar.bz2.hash"
    if container_hash_path.exists():
        with open(container_hash_path, 'r') as hash_file:
            container_hash = hash_file.readline()
            return container_hash == tmp_hash
    return False


def unpack(container, path):
    """
    Unpack a container usable by uchroot.

    Method that checks if a directory for the container exists,
    checks if erlent support is needed and then unpacks the
    container accordingly.

    Args:
        path: The location where the container is, that needs to be unpacked.

    """
    from benchbuild.utils import run
    from benchbuild.utils.uchroot import no_args

    path = local.path(path)
    c_filename = local.path(container.filename)
    name = c_filename.basename

    if not path.exists():
        path.mkdir()

    with local.cwd(path):
        Wget(container.remote, name)

        uchroot = no_args()
        uchroot = uchroot["-E", "-A", "-C", "-r", "/", "-w",
                          os.path.abspath("."), "--"]

        # Check, if we need erlent support for this archive.
        has_erlent = bash[
            "-c",
            "tar --list -f './{0}' | grep --silent '.erlent'".format(name)]
        has_erlent = (has_erlent & TF)

        untar = local["/bin/tar"]["xf", "./" + name]
        if not has_erlent:
            untar = uchroot[untar]

        untar = run.watch(untar)
        untar("--exclude=dev/*")
        if not os.path.samefile(name, container.filename):
            rm(name)
        else:
            LOG.warning("File contents do not match: %s != %s", name,
                        container.filename)
        cp(container.filename + ".hash", path)


def in_container():
    """Check, whether we are running inside a container."""
    p = local.path("/.benchbuild-container")
    return p.exists()
