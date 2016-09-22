"""Gather version information for BB."""

from os import path
from plumbum import local
from benchbuild.utils.cmd import git

from benchbuild.settings import CFG
from benchbuild.utils.downloader import get_hash_of_dirs


def is_git_root(url):
    """Checks whether an url is the root of a git repository."""
    check_path = path.join(url, ".git")
    return path.exists(check_path) and path.isdir(check_path)


def has_hash_file(url):
    check_path = url + ".hash"
    return path.exists(check_path) and path.isfile(check_path)


def get_hash_from_file(url):
    check_path = url + ".hash"
    h = None
    with open(check_path, 'r') as hf:
        h = hf.readline()
    return h


def get_git_hash(from_url):
    """
    Get the git commit hash of HEAD from :from_url.

    Args:
        from_url: The file system url of our git repository.

    Returns:
        git commit hash of HEAD, or empty string.
    """
    if from_url is None:
        return ""

    if not path.exists(from_url):
        return ""

    with local.cwd(from_url):
        return git("rev-parse", "HEAD", retcode=None)


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
    import logging as l

    l.debug("get_version_from_cache_dir")
    tmp_dir = CFG["tmp_dir"].value()
    if path.exists(tmp_dir):
        cache_path = path.join(tmp_dir, src_file)
        if is_git_root(cache_path):
            dir_hash = get_git_hash(cache_path)
        elif has_hash_file(cache_path):
            dir_hash = get_hash_from_file(cache_path)
        else:
            dir_hash = get_hash_of_dirs(cache_path)

        if dir_hash is None:
            return None
        elif len(str(dir_hash)) <= 7:
            return str(dir_hash)
        else:
            return str(dir_hash)[:7]
    else:
        return None


LLVM_VERSION = get_git_hash(str(CFG["llvm"]["src"]))
CLANG_VERSION = get_git_hash(path.join(str(CFG["llvm"]["src"]), "tools",
                                       "clang"))
POLLY_VERSION = get_git_hash(path.join(str(CFG["llvm"]["src"]), "tools",
                                       "polly"))
POLLI_VERSION = get_git_hash(path.join(str(CFG["llvm"]["src"]), "tools",
                                       "polly", "tools", "polli"))
