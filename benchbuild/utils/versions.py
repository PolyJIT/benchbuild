"""Gather version information for BB."""

from os import path

from plumbum import local

from benchbuild.settings import CFG
from benchbuild.utils.download import get_hash_of_dirs


def get_version_from_cache_dir(src_file):
    """
    Creates a version for a project out of the hash.

    The hash is taken from the directory of the source file.

    Args:
        src_file: The source file of the project using this function.

    Returns:
        Either returns the first 8 digits of the hash as string,
        the entire hash as a string if the hash consists out of less
        than 7 digits or None if the path is incorrect.
    """
    if src_file is None:
        return None

    tmp_dir = local.path(str(CFG["tmp_dir"]))
    if tmp_dir.exists():
        cache_file = tmp_dir / src_file
        dir_hash = get_hash_of_dirs(cache_file)
        if dir_hash is None:
            return None
        if len(str(dir_hash)) <= 7:
            return str(dir_hash)
        return str(dir_hash)[:7]
    return None


def get_git_hash(from_url):
    """
    Get the git commit hash of HEAD from :from_url.

    Args:
        from_url: The file system url of our git repository.

    Returns:
        git commit hash of HEAD, or empty string.
    """
    from benchbuild.utils.cmd import git
    if from_url is None:
        return ""

    if not path.exists(from_url):
        return ""

    with local.cwd(from_url):
        return git("rev-parse", "HEAD", retcode=None)
