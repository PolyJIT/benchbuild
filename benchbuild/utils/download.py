"""
# Downloading helper functions for benchbuild.

The helpers defined in this module provide access to some common Downloading
methods for the source code of benchbuild projects.
All downloads will be cached in BB_TMP_DIR and locked down with a hash that
is generated after the first download. If the hash matches the file/folder
found in BB_TMP_DIR, nothing will be downloaded at all.

Supported methods:
        Copy, CopyNoFail, Wget, Git, Svn, Rsync
"""
import hashlib
import logging
import os
from typing import Callable, List, Optional, Type

from plumbum import local

from benchbuild.settings import CFG
from benchbuild.utils.path import flocked

LOG = logging.getLogger(__name__)

AnyC = Type[object]


def get_hash_of_dirs(directory: str) -> str:
    """
    Recursively hash the contents of the given directory.

    Args:
        directory (str): The root directory we want to hash.

    Returns:
        A hash of all the contents in the directory.
    """
    sha = hashlib.sha512()
    if not os.path.exists(directory):
        raise ValueError('Directory does not exist')

    for root, _, files in os.walk(directory):
        for name in files:
            filepath = local.path(root) / name
            if filepath.exists():
                with open(filepath, 'rb') as next_file:
                    for line in next_file:
                        sha.update(line)
    return sha.hexdigest()


def source_required(src_file: local.path) -> bool:
    """
    Check, if a download is required.

    Args:
        src_file: The filename to check for.
        src_root: The path we find the file in.

    Returns:
        True, if we need to download something, False otherwise.
    """
    if not src_file.exists():
        return True

    required = True
    hash_file = src_file.with_suffix(".hash", depth=0)
    LOG.debug("Hash file location: %s", hash_file)
    if hash_file.exists():
        new_hash = get_hash_of_dirs(src_file)
        with open(hash_file, 'r') as h_file:
            old_hash = h_file.readline()
        required = not new_hash == old_hash
        if required:
            from benchbuild.utils.cmd import rm
            rm("-r", src_file)
            rm(hash_file)
    if required:
        LOG.info("Source required for: %s", src_file)
        LOG.debug(
            "Reason: src-exists: %s hash-exists: %s", src_file.exists(),
            hash_file.exists()
        )
    return required


def update_hash(src_file: local.path) -> str:
    """
    Update the hash for the given file.

    Args:
        src: The file name.
        root: The path of the given file.
    """
    hash_file = local.path(src_file) + ".hash"
    with open(hash_file, 'w') as h_file:
        new_hash = get_hash_of_dirs(src_file)
        h_file.write(str(new_hash))
    return new_hash


def Copy(From, To):
    """
    Small copy wrapper.

    Args:
        From (str): Path to the SOURCE.
        To (str): Path to the TARGET.
    """
    from benchbuild.utils.cmd import cp
    cp("-ar", "--reflink=auto", From, To)


def CopyNoFail(src, root=None):
    """
    Just copy fName into the current working directory, if it exists.

    No action is executed, if fName does not exist. No Hash is checked.

    Args:
        src: The filename we want to copy to '.'.
        root: The optional source dir we should pull fName from. Defaults
            to benchbuild.settings.CFG["tmpdir"].

    Returns:
        True, if we copied something.
    """
    if root is None:
        root = str(CFG["tmp_dir"])
    src_path = local.path(root) / src

    if src_path.exists():
        Copy(src_path, '.')
        return True
    return False


def Wget(src_url, tgt_name, tgt_root=None):
    """
    Download url, if required.

    Args:
        src_url (str): Our SOURCE url.
        tgt_name (str): The filename we want to have on disk.
        tgt_root (str): The TARGET directory for the download.
            Defaults to ``CFG["tmpdir"]``.
    """
    if tgt_root is None:
        tgt_root = str(CFG["tmp_dir"])

    from benchbuild.utils.cmd import wget

    tgt_file = local.path(tgt_root) / tgt_name
    if not source_required(tgt_file):
        Copy(tgt_file, ".")
        return

    wget(src_url, "-O", tgt_file)
    update_hash(tgt_file)
    Copy(tgt_file, ".")


def with_wget(url_dict=None, target_file=None):
    """
    Decorate a project class with wget-based version information.

    This adds two attributes to a project class:
        - A `versions` method that returns a list of available versions
          for this project.
        - A `repository` attribute that provides a repository string to
          download from later.
    We use the `git rev-list` subcommand to list available versions.

    Args:
        url_dict (dict): A dictionary that assigns a version to a download URL.
        target_file (str): An optional path where we should put the clone.
            If unspecified, we will use the `SRC_FILE` attribute of
            the decorated class.
    """

    def wget_decorator(cls):

        def download_impl(self):
            """Download the selected version from the url_dict value."""
            t_file = target_file if target_file else self.SRC_FILE
            t_version = url_dict[self.version]
            Wget(t_version, t_file)

        @staticmethod
        def versions_impl():
            """Return a list of versions from the url_dict keys."""
            return list(url_dict.keys())

        cls.versions = versions_impl
        cls.download = download_impl
        return cls

    return wget_decorator


def __clone_needed__(repository: str, directory: str) -> bool:
    """
    Do we need to create a fresh clone of the given repository.

    Args:
        repository: the repository we want to clone.
        directory: the directory we expect the clone to live.

    Returns:
        True, if the clone is required.
        False, if the directory is a valid clone.
    """
    from benchbuild.utils.cmd import git, rm

    git_dir = local.path(directory) / '.git'
    if not git_dir.exists():
        return True

    requires_clone = True
    with local.cwd(directory):
        repo_origin_url = git('config', '--get', 'remote.origin.url')
        requires_clone = repo_origin_url.strip('\n') != repository

    if requires_clone:
        rm('-r', directory)
    return requires_clone


def Git(
    repository: str,
    directory: str,
    rev: str = '',
    prefix: str = '',
    shallow_clone: bool = True
) -> str:
    """
    Get a clone of the given repo

    Args:
        repository (str): Git URL of the SOURCE repo.
        directory (str): Name of the repo folder on disk.
        rev (str): A revision to check out.
        prefix (str): TARGET folder for the git repo.
            Defaults to ``CFG["tmpdir"]``
        shallow_clone (bool): Only clone the repository shallow
            Defaults to true
    """
    repository_loc = str(prefix)
    if not prefix:
        repository_loc = str(CFG["tmp_dir"])

    src_dir = local.path(repository_loc) / directory
    tgt_dir = local.path(local.cwd) / directory
    lock_f = local.path(repository_loc + directory + '.lock')

    extra_param = []
    if shallow_clone:
        extra_param.append("--depth")
        extra_param.append("1")

    from benchbuild.utils.cmd import git, mkdir
    if __clone_needed__(repository, src_dir):
        git("clone", extra_param, repository, src_dir)
    else:
        worktree_rev = rev if rev else 'HEAD'
        with local.cwd(src_dir):
            mkdir('-p', tgt_dir)
            with flocked(lock_f):
                git('worktree', 'prune')
                git('worktree', 'add', '--detach', tgt_dir, worktree_rev)

    return repository_loc


def with_git(
    repo: str,
    target_dir: Optional[str] = None,
    limit: Optional[int] = None,
    refspec: str = "HEAD",
    clone: bool = True,
    rev_list_args: Optional[List[str]] = None,
    shallow_clone: bool = True,
    version_filter: Callable[[str], bool] = lambda version: True
) -> Callable[[AnyC], AnyC]:
    """
    Decorate a project class with git-based version information.

    This adds two attributes to a project class:
        - A `versions` method that returns a list of available versions
          for this project.
        - A `repository` attribute that provides a repository string to
          download from later.
    We use the `git rev-list` subcommand to list available versions.

    Args:
        repo (str): Repository to download from, this will be stored
            in the `repository` attribute of the decorated class.
        target_dir (str): An optional path where we should put the clone.
            If unspecified, we will use the `SRC_FILE` attribute of
            the decorated class.
        limit (int): Limit the number of commits to consider for available
            versions. Versions are 'ordered' from latest to oldest.
        refspec (str): A git refspec string to start listing the versions from.
        clone (bool): Should we clone the repo if it isn't already available
            in our tmp dir? Defaults to `True`. You can set this to False to
            avoid time consuming clones, when the project has not been accessed
            at least once in your installation.
        ref_list_args (list of str): Additional arguments you want to pass to
            `git rev-list`.
        shallow_clone (bool): Only clone the repository shallow
            Defaults to true
        version_filter (class filter): Filter function to remove unwanted
            project versions.

    """
    if not rev_list_args:
        rev_list_args = []

    def git_decorator(cls):
        from benchbuild.utils.cmd import git

        @staticmethod
        def versions_impl():
            """Return a list of versions from the git hashes up to :limit:."""
            directory = cls.SRC_FILE if target_dir is None else target_dir
            repo_prefix = local.path(str(CFG["tmp_dir"]))
            repo_loc = local.path(repo_prefix) / directory
            if __clone_needed__(repo, repo_loc):
                if not clone:
                    return []
                git("clone", repo, repo_loc)

            with local.cwd(repo_loc):
                rev_list = git(
                    "rev-list", "--abbrev-commit", "--abbrev=10", refspec,
                    *rev_list_args
                ).strip().split('\n')
                git("rev-parse", "--short=10", refspec).strip().split('\n')

            if limit:
                return list(filter(version_filter, rev_list))[:limit]

            return list(filter(version_filter, rev_list))

        def download_impl(self):
            """Download the selected version."""
            nonlocal target_dir, git
            directory = cls.SRC_FILE if target_dir is None else target_dir
            Git(
                self.repository,
                directory,
                self.version,
                shallow_clone=shallow_clone
            )

        cls.versions = versions_impl
        cls.download = download_impl
        cls.repository = repo
        return cls

    return git_decorator


def Svn(url, fname, to=None):
    """
    Checkout the SVN repo.

    Args:
        url (str): The SVN SOURCE repo.
        fname (str): The name of the repo on disk.
        to (str): The name of the TARGET folder on disk.
            Defaults to ``CFG["tmpdir"]``
    """
    if to is None:
        to = str(CFG["tmp_dir"])

    src_dir = local.path(to) / fname
    if not source_required(src_dir):
        Copy(src_dir, ".")
        return

    from benchbuild.utils.cmd import svn
    svn("co", url, src_dir)
    update_hash(src_dir)
    Copy(src_dir, ".")


def Rsync(url, tgt_name, tgt_root=None):
    """
    RSync a folder.

    Args:
        url (str): The url of the SOURCE location.
        fname (str): The name of the TARGET.
        to (str): Path of the target location.
            Defaults to ``CFG["tmpdir"]``.
    """
    if tgt_root is None:
        tgt_root = str(CFG["tmp_dir"])

    from benchbuild.utils.cmd import rsync

    tgt_dir = local.path(tgt_root) / tgt_name
    if not source_required(tgt_dir):
        Copy(tgt_dir, ".")
        return

    rsync("-a", url, tgt_dir)
    update_hash(tgt_dir)
    Copy(tgt_dir, ".")
