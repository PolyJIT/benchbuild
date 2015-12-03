#!/usr/bin/env python
"""
Gather version information for PPROF.
"""

from plumbum import local
from plumbum.cmd import git

from pprof.settings import config
from os import path


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


LLVM_VERSION = get_git_hash(config["llvm-srcdir"])
CLANG_VERSION = get_git_hash(path.join(config["llvm-srcdir"], "tools",
                                       "clang"))
POLLY_VERSION = get_git_hash(path.join(config["llvm-srcdir"], "tools",
                                       "polly"))
POLLI_VERSION = get_git_hash(path.join(config["llvm-srcdir"], "tools", "polly",
                                       "tools", "polli"))
