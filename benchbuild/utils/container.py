"""
Container utilites.
"""
import os
import logging
from benchbuild.settings import CFG
from benchbuild.utils.cmd import cp, mkdir, bash, rm, curl, tail, cut
from benchbuild.utils.downloader import Wget
from plumbum import local, TF

LOG = logging.getLogger(__name__)


def cached(func):
    ret = None

    def call_or_cache(*args, **kwargs):
        nonlocal ret
        if ret is None:
            ret = func(*args, **kwargs)
        return ret

    return call_or_cache


def is_valid_container(container, path):
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

    container_hash_path = os.path.abspath(os.path.join(path,
                                                       "gentoo.tar.bz2.hash"))
    if not os.path.exists(container_hash_path):
        return False
    else:
        with open(container_hash_path, 'r') as hash_file:
            container_hash = hash_file.readline()
            return container_hash == tmp_hash


def unpack_container(container, path):
    """
    Unpack a container usable by uchroot.

    Method that checks if a directory for the container exists,
    checks if erlent support is needed and then unpacks the
    container accordingly.

    Args:
        path: The location where the container is, that needs to be unpacked.

    """
    from benchbuild.utils.run import run, uchroot_no_args

    path = os.path.abspath(path)
    name = os.path.basename(os.path.abspath(container.filename))
    if not os.path.exists(path):
        mkdir("-p", path)

    with local.cwd(path):
        Wget(container.remote, name)

        uchroot = uchroot_no_args()
        uchroot = uchroot["-E", "-A", "-C", "-r", "/", "-w",
                          os.path.abspath("."), "--"]

        # Check, if we need erlent support for this archive.
        has_erlent = bash[
            "-c", "tar --list -f './{0}' | grep --silent '.erlent'".format(
                name)]
        has_erlent = (has_erlent & TF)

        cmd = local["/bin/tar"]["xf"]
        if not has_erlent:
            cmd = uchroot[cmd["./" + name]]
        else:
            cmd = cmd[name]

        run(cmd["--exclude=dev/*"])
        if not os.path.samefile(name, container.filename):
            rm(name)
        else:
            LOG.warning("File contents do not match: %s != %s",
                        name, container.filename)
        cp(container.filename + ".hash", path)


class Container(object):
    name = "container"

    @property
    def remote(self):
        pass

    @property
    def filename(self):
        image_cfg = CFG["container"]["images"].value()
        image_cfg = image_cfg[self.name]
        if os.path.isabs(image_cfg):
            return image_cfg
        else:
            return os.path.join(CFG["tmp_dir"].value(), image_cfg)

    @property
    def local(self):
        """
        Finds the current location of a container.
        Also unpacks the project if necessary.

        Returns:
            target: The path, where the container lies in the end.
        """
        from benchbuild.settings import CFG
        assert self.name in CFG["container"]["images"].value()
        target = os.path.join(CFG["tmp_dir"].value(), self.name)

        if not os.path.exists(target) or not is_valid_container(self, target):
            unpack_container(self, target)

        return target


class Gentoo(Container):
    name = "gentoo"

    @cached
    def latest_src_uri(self):
        """
        Get the latest src_uri for a stage 3 tarball.

        Returns (str):
            Latest src_uri from gentoo's distfiles mirror.
        """
        from plumbum import ProcessExecutionError

        latest_txt = "http://distfiles.gentoo.org/releases/amd64/autobuilds/"\
                     "latest-stage3-amd64.txt"
        try:
            src_uri = (curl[latest_txt] |
                       tail["-n", "+3"] |
                       cut["-f1", "-d "])().strip()
        except ProcessExecutionError as proc_ex:
            src_uri = "NOT-FOUND"
            LOG.error(
                "Could not determine latest stage3 src uri: %s", str(proc_ex))
        return src_uri

    @property
    def remote(self):
        """Get a remote URL of the requested container."""
        return "http://distfiles.gentoo.org/releases/amd64/autobuilds/{0}" \
            .format(self.latest_src_uri())


class Ubuntu(Container):
    name = "ubuntu"

    @property
    def remote(self):
        """Get a remote URL of the requested container."""
        pass
