"""
Container utilites.
"""
import os
import logging
from benchbuild import settings as s
from benchbuild.utils.cmd import cp, mkdir, bash, rm, curl, tail, cut
from benchbuild.utils.downloader import Wget
from plumbum import local, TF

__CONTAINER_PATH_SUFFIX__ = "container"
__CONTAINER_DEFAULT__ = os.path.abspath(os.path.join(s.CFG["tmp_dir"].value(),
                                        "gentoo.tar.bz2"))


def cached(func):
    ret = None

    def call_or_cache(*args, **kwargs):
        nonlocal ret
        if ret is None:
            ret = func(*args, **kwargs)
        return ret

    return call_or_cache


@cached
def latest_src_uri():
    """
    Get the latest src_uri for a stage 3 tarball.

    Returns (str):
        Latest src_uri from gentoo's distfiles mirror.
    """
    from plumbum import ProcessExecutionError
    from logging import error

    latest_txt = "http://distfiles.gentoo.org/releases/amd64/autobuilds/"\
                 "latest-stage3-amd64.txt"
    try:
        src_uri = (curl[latest_txt] |
                   tail["-n", "+3"] |
                   cut["-f1", "-d "])().strip()
    except ProcessExecutionError as proc_ex:
        src_uri = "NOT-FOUND"
        error("Could not determine latest stage3 src uri: {0}", str(proc_ex))
    return src_uri


def get_container_url():
    """Fetches the lates src_uri from the gentoo mirrors."""
    return "http://distfiles.gentoo.org/releases/amd64/autobuilds/{0}" \
        .format(latest_src_uri())

def get_base_dir():
    """
    Method that finds out the path of the read-only container for a project.
    Basically just get_path_of_container but with a different name for clear
    seperation between the situations in which it is used.

    Returns:
        An absolute path of the base directory.
    """
#Change later on, in case of multiple containers and adjust the container of
#a project according to his prefered container
    return os.path.abspath(get_path_of_container())


def is_valid_container(path):
    """
    Checks if a container exists and is unpacked.

    Args:
        path: The location where the container is expected.

    Returns:
        True if the container is valid, False if the container needs to
        unpacked or if the path does not exist yet.
    """
    try:
        tmp_hash_path = __CONTAINER_DEFAULT__ + ".hash"
        with open(tmp_hash_path, 'r') as tmp_file:
            tmp_hash = tmp_file.readline()
    except IOError:
        logger = logging.getLogger(__name__)
        logger.info("No .hash-file in the tmp-directory.")

    container_hash_path = os.path.abspath(os.path.join(path,
                                                       "gentoo.tar.bz2.hash"))
    if not os.path.exists(container_hash_path):
        return False
    else:
        with open(container_hash_path, 'r') as hash_file:
            container_hash = hash_file.readline()
            return container_hash == tmp_hash

def unpack_container(path):
    """
    Method that checks if a directory for the container exists,
    checks if erlent support is needed and then unpacks the
    container accordingly.

    Args:
        path: The location where the container is, that needs to be unpacked.

    """
    from benchbuild.utils.run import run, uchroot_no_args

    if not os.path.exists(path):
        mkdir("-p", path)

    path = os.path.abspath(path)
    local_container = os.path.basename(__CONTAINER_DEFAULT__)

    with local.cwd(path):
        Wget(get_container_url(), __CONTAINER_DEFAULT__)
        cp(__CONTAINER_DEFAULT__ + ".hash", path)

        uchroot = uchroot_no_args()
        uchroot = uchroot["-E", "-A", "-C", "-r", "/", "-w", os.path.abspath(
            "."), "--"]

        # Check, if we need erlent support for this archive.
        has_erlent = bash[
            "-c", "tar --list -f './{0}' | grep --silent '.erlent'".format(
                local_container)]
        has_erlent = (has_erlent & TF)

        cmd = local["/bin/tar"]["xf"]
        if not has_erlent:
            cmd = uchroot[cmd["./" + local_container]]
        else:
            cmd = cmd[local_container]

        run(cmd["--exclude=dev/*"])
        if not os.path.samefile(local_container, __CONTAINER_DEFAULT__):
            rm(local_container)

def get_path_of_container():
    """
    Finds the current location of a container.
    Also unpacks the project if necessary.

    Returns:
        target: The path, where the container lies in the end.
    """
    target = os.path.join(s.CFG["tmp_dir"].value(), __CONTAINER_PATH_SUFFIX__)
    if not os.path.exists(target) or not is_valid_container(target):
        unpack_container(target)

    return target
